import pathlib
import psycopg2
import tomli
import random
from datetime import datetime, timedelta

data_path = pathlib.Path(__file__).parent /"data.toml"
data = tomli.loads(data_path.read_text())
customers = data["customers"]["customer"]
markets = data["markets"]["market"]
logistics = data["vehicles"]["vehicle"]
reps = data["reps"]["rep"]
products = data["products"]["product"]

def create_table(table_name, columns):
    with psycopg2.connect(dbname="analytics", host="localhost", port=5432, user="db_user", password="user_password") as conn:
        with conn.cursor as cur:
            cur.execute(f"""
                create table if not exists {table_name}(
                {','.join(columns)})""")

def load_table(table_name, data):
    with psycopg2.connect(dbname="analytics", host="localhost", port=5432, user="db_user", password="userpassword") as conn:
        with conn.cursor as cur:
            cur.executemany(f"""
                insert into {table_name} values(
                {', '.join(['%s'] * len(data[0]))})""", data)
            conn.commit()

def get_last_invoice_number():
    with psycopg2.connect(dbname="analytics", host="localhost", port=5432, user="db_user", password="userpassword") as conn:
        with conn.cursor as cur:
            cur.execute("select count(distinct invoice_number) from sales")
            result = cur.fetchone()[0]
            return result if result else 0

def generate_sales_data():
    last_invoice_number = get_last_invoice_number()
    new_invoice_number = last_invoice_number + 1
    invoice_number = f"INV{new_invoice_number:0005d}"
    customer = random.choice(customers)
    num_products = random.randint(1, len(products))
    selected_products = random.sample(products, num_products)

    sales_data = []
    invoice_data = []
    for product in selected_products:
        quantity = random.randint(1,10)
        price = product["price"]
        weight = product["weight"]
        total_price = quantity * price
        total_weight = quantity * weight
        start_date = datetime(2023,1,1)
        end_date = datetime(2023, 12, 31)
        invoice_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        invoice_time = datetime.strptime(f"{random.randint(0,23)}:{random.randint(0,59)}", "%H:%M")

        sales_data.append((customer["crm"],invoice_number,invoice_date.date(),total_price, total_weight))
        invoice_data.append((invoice_number,start_date.date(),invoice_time.time(),product["p_code"],price,quantity,total_price,weight,total_weight))
    create_table("sales", 
                ["crm VARCHAR(255)",
                "invoice_number VARCHAR(255)",
                "invoice_date DATE",
                "total_price FLOAT",
                "total_weight FLOAT",])
    create_table("invoices", 
                ["invoice_number VARCHAR(255)",
                "invoice_date DATE",
                "invoice_time TIME",
                "product_code VARCHAR(255)",
                "price FLOAT",
                "quantity INTEGER",
                "total_price FLOAT",
                "weight FLOAT",
                "total_weight FLOAT"])
    load_table("sales", sales_data)
    load_table("invoices", invoice_data)

def generate_delivery_data():
    pass

def generate_accounts_data():
    pass

def generate_products_data():
    products_data = []
    for product_data in products:
        name = product_data.get("p_name", None)
        code = product_data.get("p_code", None)
        weight = product_data.get("weight", None)
        price = product_data.get("price", None)
        products_data.append((name,code,weight,price))
    create_table("products",
                 ["name VARCHAR(255)",
                  "code VARCHAR(255)",
                  "weight FLOAT",
                  "price FLOAT"])
    load_table("products", products_data)

def generate_customer_data():
    customers_data = []
    for customer_data in customers:
        crm = customer_data.get("crm", None)
        phone = customer_data.get("phone", None)
        route = customer_data.get("route", None)
        customers_data.append((crm, phone, route))

    create_table("customers",
                 ["crm VARCHAR(255)",
                  "phone INTEGER",
                  "route VARCHAR(255)"])
    load_table("customers", customers_data)

def generate_reps_data():
    reps_data = []
    for rep_data in reps:
        name = rep_data.get("name", None)
        market = rep_data.get("market", None)
        reps_data.append((name, market))
    
    create_table("sales_reps",
                 ["rep_name VARCHAR(255)",
                  "market VARCHAR(255)"])
    load_table("sales_reps", reps_data)

def generate_markets_data():
    markets_data = []
    for market_data in markets:
        name = market_data.get("name", None)
        route = market_data.get("route", None)
        longitude = market_data.get("longitude", None)
        latitude = market_data.get("latitude", None)
        market_data.append((name, route, longitude, latitude))

    create_table("markets",
                 ["name VARCHAR(255)",
                  "route VARCHAR(255)",
                  "longitude FLOAT",
                  "latitude FLOAT"])
    load_table("markets", markets_data)

def generate_logistics_data():
    vehicles_data = []
    for vehicle_data in logistics:
        reg_no = vehicle_data.get("reg",None)
        tonnage = vehicle_data.get("tonnage", None)
        vehicles_data.append((reg_no,tonnage))

        create_table("logistics",
                     ["reg_no VARCHAR(255)",
                      "tonnage FLOAT"])
        load_table("logistics", vehicles_data)


