from datetime import datetime, timedelta
import pathlib
import psycopg2
import tomli
import random

DB_CONFIG = {
    "dbname": "analytics",
    "host": "localhost",
    "port": 5432,
    "user": "db_user",
    "password": "user_password"
}

data_path = pathlib.Path(__file__).parent /"data.toml"
data = tomli.loads(data_path.read_text())
customers = data["customers"]["customer"]
markets = data["markets"]["market"]
logistics = data["vehicles"]["vehicle"]
reps = data["reps"]["rep"]
products = data["products"]["product"]
inv = 0

def connect_db():
    return psycopg2.connect(**DB_CONFIG)

def create_table(table_name, columns):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                create table if not exists {table_name}(
                {','.join(columns)})""")

def load_table(table_name, data):
    with connect_db() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(f"begin; truncate table {table_name}; commit;")
                cur.executemany(f"insert into {table_name} values ({', '.join(['%s'] * len(data[0]))})", data)
            except Exception as e:
                conn.rollback()
                raise e
            else:
                conn.commit()

def get_last_invoice_number():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("select max(cast(substring(invoice_number from 4) as integer)) from invoices")
            result = cur.fetchone()[0]
            return result if result else 0

def get_sales_data():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("select crm, invoice_number, invoice_date, sum(total_price) as total_price, sum(total_weight) as total_weight from invoices group by crm, invoice_number, invoice_date")
            sales = cur.fetchall()
            return sales

def get_delivery_data():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("select invoice_number, invoice_date, sum(total_weight) as total_weight from invoices group by invoice_number, invoice_date order by invoice_number")
            result = cur.fetchall()
            return result

def get_accounts_data():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("select invoice_number, invoice_date, sum(total_price) as total_price from invoices group by invoice_number, invoice_date order by invoice_number")
            sales = cur.fetchall()
            return sales

def generate_accounts_data():
    data = get_accounts_data()
    accounts_data = []

    for acc_data in data:
        invoice_number, invoice_date, total_price = acc_data
        payment_amount = random.uniform(max(total_price - 7000, 0), total_price)
        payment_date = invoice_date + timedelta(days=random.randint(0, 2))
        payment_date_str = payment_date.strftime("%Y-%m-%d")
        accounts_data.append((invoice_number, invoice_date, total_price, payment_amount, payment_date_str))
    
    create_table("accounts",
                 ["invoice_number VARCHAR(255)",
                  "invoice_date DATE",
                  "total_price FLOAT",
                  "payment_amount FLOAT",
                  "payment_date DATE"])
    load_table("accounts", accounts_data)

def generate_delivery_data():
    data = get_delivery_data()
    delivery_data = []
    current_vehicle_index = 0
    current_vehicle_capacity = 0

    for del_data in data:
        invoice_number, invoice_date, total_weight = del_data
        vehicle = logistics[current_vehicle_index]
        if current_vehicle_capacity + total_weight <= vehicle["tonnage"] * 1000:
            delivery_data.append((invoice_number, invoice_date, total_weight, vehicle["reg"]))
            current_vehicle_capacity += total_weight
        else:
            current_vehicle_index = (current_vehicle_index + 1) % len(logistics)
            current_vehicle_capacity = total_weight
            delivery_data.append((invoice_number, invoice_date, total_weight, logistics[current_vehicle_index]["reg"]))
    create_table("deliveries",
                 ["invoice_number VARCHAR(255)",
                  "invoice_date DATE",
                  "total_weight FLOAT",
                  "vehicle VARCHAR(255)"])
    load_table("deliveries", delivery_data)

def generate_sales_data():
    data = get_sales_data()
    sales_data = []
    for sale_data in data:
        sales_data.append(sale_data)
    create_table("sales",
                 ["crm VARCHAR(255)",
                  "invoice_number VARCHAR(255)",
                  "invoice_date DATE",
                  "total_price FLOAT",
                  "total_weight FLOAT"])
    load_table("sales", sales_data)

def generate_invoice_data():
    global inv
    inv += 1
    invoice_number = f"INV{inv:04d}"
    customer = random.choice(customers)
    num_products = random.randint(1, len(products))
    selected_products = random.sample(products, num_products)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    invoice_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    invoice_time = datetime.strptime(f"{random.randint(7, 18)}:{random.randint(0, 59)}", "%H:%M")
    
    invoice_data = []
    for product in selected_products:
        quantity = random.randint(1, 10)
        price = product["price"]
        weight = product["weight"]
        total_price = quantity * price
        total_weight = quantity * weight
        invoice_data.append((customer["crm"], invoice_number, invoice_date.date(), invoice_time.time(), product["p_code"], price,
                             quantity, total_price, weight, total_weight))

    return invoice_data

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
                  "code VARCHAR(255) UNIQUE",
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
                 ["crm VARCHAR(255) UNIQUE",
                  "phone BIGINT UNIQUE",
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
        markets_data.append((name, route, longitude, latitude))

    create_table("markets",
                 ["name VARCHAR(255)",
                  "route VARCHAR(255) UNIQUE",
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
                    ["reg_no VARCHAR(255) UNIQUE",
                      "tonnage FLOAT"])
    load_table("logistics", vehicles_data)


generate_products_data()
generate_customer_data()
generate_reps_data()
generate_markets_data()
generate_logistics_data()
create_table("invoices",
             ["crm VARCHAR(255)",
              "invoice_number VARCHAR(255)",
              "invoice_date DATE",
              "invoice_time TIME",
              "product_code VARCHAR(255)",
              "price FLOAT",
              "quantity INTEGER",
              "total_price FLOAT",
              "weight FLOAT",
              "total_weight FLOAT"])
for _ in range(1000):
    invoices = generate_invoice_data()
    load_table("invoices", invoices)
generate_sales_data()
generate_delivery_data()
generate_accounts_data()

