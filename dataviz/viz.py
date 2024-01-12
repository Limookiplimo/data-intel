import streamlit as st
import psycopg2
import pandas as pd

DB_CONFIG = {
    "dbname": "analytics",
    "host": "localhost",
    "port": 5432,
    "user": "db_user",
    "password": "user_password"
}

st.title("Retail Analytics")

def connect_db():
    return psycopg2.connect(**DB_CONFIG)

@st.cache_data
def get_data():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""select s.crm, s.invoice_number, s.invoice_date, s.total_price, s.total_weight, 
                           payment_amount, payment_date, phone, m.route, rep_name
                from sales s
                join accounts a on a.invoice_number = s.invoice_number
                join customers c on c.crm  = s.crm 
                join deliveries d on d.invoice_number = s.invoice_number 
                join markets m on m.route = c.route
                join sales_reps sr on sr.market = m.name""")
            return cur.fetchall()

def create_pandas_dataframe():
    data = get_data()
    cols = ["crm","invoice_number","invoice_date","total_price","total_weight","payment_amount","payment_date","phone","route","rep_name"]
    df = pd.DataFrame(data, columns=cols)
    sales_by_route = df.groupby('route')['total_price'].sum()
    st.write(sales_by_route)

if __name__ == "__main__":
    results = create_pandas_dataframe()
    results


