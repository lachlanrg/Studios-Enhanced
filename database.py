from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()
import MySQLdb
import os
import mysql.connector


db_username = os.getenv('USERNAME')
db_password = os.getenv('PASSWORD')
db_host = os.getenv('HOST')
db_name = os.getenv('DATABASE')

# Create the connection string using the values from the .env file
dbconnection_string = f"mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"

#instead of "ca": "insert cert"
engine = create_engine (
    dbconnection_string, pool_pre_ping=True,
    connect_args= {
        "ssl": {
            "ssl_cert": "/Users/lachlangreig/Documents/Studios-Enhanced/cert.pem"
        }

    }
)

def load_products_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("select * from products"))
        column_names = result.keys()
    
        products = []
        for row in result.all():
            products.append(dict(zip(column_names, row)))
        return products
    

def load_product_from_db(id):
    with engine.connect() as conn:
        result = conn.execute(text("select * from products where id=:val"), val=id)
        rows = result.all()
        if len(rows) == 0:
            return None
        else: 
            return dict(rows[0])
        
def get_product_by_id(id):
    db = mysql.connector.connect(
        host= os.getenv('HOST'),
        user=os.getenv('USERNAME'),  
        passwd=os.getenv('PASSWORD'),  
        database=os.getenv('DATABASE') 
    )
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM products WHERE id = %s"
    cursor.execute(query, (id,))
    product = cursor.fetchone()
    cursor.close()
    db.close()
    return product

def update_current_product(user_id, product_id):
    db = mysql.connector.connect(
        host= os.getenv('HOST'),
        user=os.getenv('USERNAME'),  
        passwd=os.getenv('PASSWORD'),  
        database=os.getenv('DATABASE') 
    )
    cursor = db.cursor(dictionary=True)
    query = "UPDATE accounts SET current_product = %s WHERE id = %s"
    cursor.execute(query, (product_id, user_id))
    db.commit()
    cursor.close()
    db.close()
   

    



    

    
    



    

