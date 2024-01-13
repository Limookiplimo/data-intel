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
    return df

@st.cache_data
def calculate_kpis():
    df = create_pandas_dataframe()
    total_sales = int(df["total_price"].sum())
    total_invoices = df["invoice_number"].count()
    total_payments = int(df["payment_amount"].sum())
    invoice_totals = df.groupby("invoice_number")[["total_price", "payment_amount"]].sum()
    pending_payments = int((invoice_totals["total_price"] - invoice_totals["payment_amount"]).sum())
    tonnage = int(df["total_weight"].sum())
    l1, l2, m, r1, r2 = st.columns(5)
    with l1:
        st.subheader("Total Sales:")
        st.subheader(f"{total_sales:,}")
    with l2:
        st.subheader("Total Payments:")
        st.subheader(f"{total_payments:,}")
    with r1:
        st.subheader("Total Tonnage:")
        st.subheader(f"{tonnage:,}")
    with r2:
        st.subheader("Pending Payments:")
        st.subheader(f"{pending_payments:,}")
    with m:
        st.subheader("Total Invoices:")
        st.subheader(f"{total_invoices:,}")
    
    st.markdown("---")

if __name__ == "__main__":
    calculate_kpis()
