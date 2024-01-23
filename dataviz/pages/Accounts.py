import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from Overview import create_pandas_dataframe

st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align: center; color: green'> ABC Acoounts</h1>", unsafe_allow_html=True)

def accounts_kpis():
    df = create_pandas_dataframe()
    total_sales = int(df["total_price"].sum())
    total_payments = int(df["payment_amount"].sum())
    collection_rate = round((total_payments / total_sales) * 100, 2)
    left_col, right_col = st.columns(2)
    with left_col:
        st.header(":blue[Sales Rep KPIs]")
        st.subheader(f"Total Sales: $ {total_sales:,}")
        st.subheader(f"Payments: $ {total_payments:,}")
        st.subheader(f"Collection Rate: {collection_rate:,}%")

    with right_col:
        st.subheader(":blue[Metrics Table]")
        df['collection_rate'] = round(df["payment_amount"] / df["total_price"] * 100)
        tabular_metrics = df.groupby(['inv_month'], as_index=False).agg({'total_price': 'sum', 'payment_amount': 'sum', 'collection_rate': 'mean'}).reset_index(drop=True)
        tabular_metrics.columns = ["Month", "Sales", "Payments", "Rate"]
        result_df = tabular_metrics.pivot_table(index=None, values=["Payments", "Sales", "Rate"], columns='Month', aggfunc='sum')
        st.write(result_df)

    st.markdown("---")

def payments_charts():
    df = create_pandas_dataframe()
    payment_trend = df.groupby("inv_month")[["payment_amount"]].sum()
    sales_payments = df.groupby("inv_month")[["payment_amount","pending_payment"]].sum()
    left_col, right_col = st.columns(2)
    with left_col:
        fig_payment_trend = px.bar(payment_trend,x=payment_trend.index,y="payment_amount",color='payment_amount',labels={'payment_amount':'Collections'},title="Collections Trend")
        fig_payment_trend.update_xaxes(title_text="Month")
        st.plotly_chart(fig_payment_trend)

    with right_col:
        fig_sales_payments = px.line(sales_payments, x=sales_payments.index, y=["payment_amount","pending_payment"], title="Collected vis Pending Payments",line_shape="linear", render_mode="svg",labels={"variable": "Collections vs Pendings"})
        fig_sales_payments.update_xaxes(title_text="Month")
        fig_sales_payments.update_yaxes(title_text="Amount")
        fig_sales_payments.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
        st.plotly_chart(fig_sales_payments) 

if __name__ == '__main__':
    accounts_kpis()
    payments_charts()