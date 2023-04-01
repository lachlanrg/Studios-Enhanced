from sqlalchemy import create_engine, text

dbconnection_string = "mysql+pymysql://p3tdqa99eyp5ihs04p9m:pscale_pw_ReSZao9FFuxG5X7dYrZu7dfL0vryGybgYNI2k7Oc7Dg@aws.connect.psdb.cloud/studiosenhanced?charset=utf8mb4"

engine = create_engine (
    dbconnection_string, pool_pre_ping=True,
    connect_args= {
        "ssl": {
            "ca": "/home/gord/client-ssl/ca.pem",
            "cert": "/home/gord/client-ssl/client-cert.pem",
            "key": "/home/gord/client-ssl/client-key.pem"
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



    

    
    



    

