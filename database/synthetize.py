import pathlib
import psycopg2
import tomli

data_path = pathlib.Path(__file__).parent /"data.toml"
data = tomli.loads(data_path.read_text())
customers = data["customers"]["customer"]
markets = data["markets"]["market"]
logistics = data["vehicles"]["vehicle"]
reps = data["reps"]["rep"]

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

def generate_delivery_data():
    pass

def generate_accounts_data():
    pass

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


