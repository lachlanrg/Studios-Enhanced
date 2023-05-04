from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()
import MySQLdb
import os


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
    



    

    
    



    

