import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

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

def get_data():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        select s.crm, s.invoice_number, s.invoice_date, extract(month from s.invoice_date) as month, 
                            s.total_price, s.total_weight, payment_amount, payment_date, phone, m.route, rep_name
                        from sales s
                        join accounts a on a.invoice_number = s.invoice_number
                        join customers c on c.crm  = s.crm 
                        join deliveries d on d.invoice_number = s.invoice_number 
                        join markets m on m.route = c.route
                        join sales_reps sr on sr.market = m.name""")
            return cur.fetchall()
        
def create_pandas_dataframe():
    data = get_data()
    cols = ["crm","invoice_number","invoice_date","month","total_price","total_weight","payment_amount","payment_date","phone","route","rep_name"]
    df = pd.DataFrame(data, columns=cols)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["payment_date"] = pd.to_datetime(df["payment_date"])
    return df

def calculate_key_performance_indicators():
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

def create_sales_payments_chart():
    df = create_pandas_dataframe()
    sales_payments = df.groupby("month")[["total_price", "payment_amount"]].sum()
    fig_sales_payments = px.line(sales_payments, x=sales_payments.index, y=['total_price', 'payment_amount'], title='Invoice Amount vis Payments Collections',
              line_shape='linear', render_mode='svg')
    fig_sales_payments.update_xaxes(title_text="Month")
    fig_sales_payments.update_yaxes(title_text='Total Sales')
    fig_sales_payments.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
    st.plotly_chart(fig_sales_payments)
    
    st.markdown("---")

if __name__ == "__main__":
    calculate_key_performance_indicators()
    create_sales_payments_chart()