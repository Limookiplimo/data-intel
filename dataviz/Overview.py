import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

DB_CONFIG = {
    "dbname": "analytics",
    "host": "localhost",
    "port": 5432,
    "user": "db_user",
    "password": "user_password"
}


st.markdown("<h1 style='text-align: center; color: green'> ABC Analytics Platform</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Retrospective analysis of ABC performance in the Market</p>", unsafe_allow_html=True)

def connect_db():
    return psycopg2.connect(**DB_CONFIG)

def get_data():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        select s.crm, s.invoice_number, s.invoice_date, extract(month from s.invoice_date) as inv_month, s.total_price, 
                            round(payment_amount) as payment_amount,round(s.total_price - payment_amount) as pending,
                            payment_date, extract(month from payment_date) as pmt_month, s.total_weight, m.route, rep_name, vehicle
                        from sales s
                        join accounts a on a.invoice_number = s.invoice_number
                        join customers c on c.crm  = s.crm 
                        join deliveries d on d.invoice_number = s.invoice_number 
                        join markets m on m.route = c.route
                        join sales_reps sr on sr.market = m.name""")
            return cur.fetchall()
        
st.cache_data()        
def create_pandas_dataframe():
    data = get_data()
    cols = ["crm","invoice_number","invoice_date","inv_month","total_price","payment_amount","pending_payment","payment_date","pmt_month","total_weight","route","rep_name","vehicle"]
    df = pd.DataFrame(data, columns=cols)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["payment_date"] = pd.to_datetime(df["payment_date"])
    df.to_csv("./dataviz/retail.csv", index=False)
    return df

st.cache_data() 
def calculate_key_performance_indicators():
    # df = create_pandas_dataframe()
    df = pd.read_csv("retail.csv")
    total_sales = int(df["total_price"].sum())
    total_invoices = df["invoice_number"].count()
    total_payments = int(df["payment_amount"].sum())
    pending_payments = int(df["pending_payment"].sum())
    tonnage = int(df["total_weight"].sum())
    st.header(":blue[Key Performance Indicators]")
    l1, l2, m, r1, r2 = st.columns(5)
    with l1:
        st.subheader("Total Sales:")
        st.subheader(f"$ {total_sales:,}")
    with l2:
        st.subheader("Total Payments:")
        st.subheader(f"$ {total_payments:,}")
    with r1:
        st.subheader("Total Tonnage:")
        st.subheader(f"{tonnage:,} t")
    with m:
        st.subheader("Pending Payments:")
        st.subheader(f"$ {pending_payments:,}")
    with r2:
        st.subheader("Total Invoices:")
        st.subheader(f"{total_invoices:,}")
    
    st.markdown("---")

st.cache_data() 
def create_sales_payments_chart():
    # df = create_pandas_dataframe()
    df = pd.read_csv("retail.csv")
    sales_payments = df.groupby("inv_month")[["total_price", "payment_amount"]].sum()
    sales_payments.columns = ["Sales","Payments"]
    payments_pendings = df.groupby("pmt_month")[["payment_amount", "pending_payment"]].sum()
    payments_pendings.columns = ["Paid", "Pending"]
    left_chart, right_chart = st.columns(2)
    with left_chart:
        fig_sales_payments = px.line(sales_payments,x=sales_payments.index,y=["Sales", "Payments"],title="Total Sales vs Total Payments",line_shape="linear",render_mode="svg",labels={"variable": "Sales vs Payments"})
        fig_sales_payments.update_xaxes(title_text="Month")
        fig_sales_payments.update_yaxes(title_text="Amount")
        fig_sales_payments.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
        st.plotly_chart(fig_sales_payments)

    with right_chart:
        fig_payments_pendings = px.line(payments_pendings, x=payments_pendings.index,y=["Paid","Pending"],title="Total Payment vs Total Pending ",line_shape="linear",render_mode="svg",labels={"variable": "Paid vs Pendings"})
        fig_payments_pendings.update_xaxes(title_text="Month")
        fig_payments_pendings.update_yaxes(title_text="Amount")
        fig_payments_pendings.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
        st.plotly_chart(fig_payments_pendings)

if __name__ == "__main__":
    calculate_key_performance_indicators()
    create_sales_payments_chart()