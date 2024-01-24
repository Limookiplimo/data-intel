import streamlit as st
import plotly.express as px
from Overview import create_pandas_dataframe
st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align: center; color: green'> ABC Sales Representatives</h1>", unsafe_allow_html=True)

def rep_selection():
    df = create_pandas_dataframe()
    rep_df = df.groupby(["rep_name","inv_month"], as_index=False).agg({"total_price":"sum","payment_amount":"sum","invoice_number":"count","route":"count"}).reset_index(drop=True)
    rep_choice = rep_df["rep_name"].unique()
    default_rep = ["Rep One"]

    for rep in default_rep:
        if rep not in rep_choice:
            default_rep.remove(rep)
    rep_name = st.multiselect("Select Representative: ", options=rep_choice, default=default_rep)
    select_df = df.query("rep_name == @rep_name")
    return select_df

def rep_kpi_metrics(df):
    total_sales = int(df["total_price"].sum())
    total_payments = int(df["payment_amount"].sum())
    total_orders = df["invoice_number"].count()
    left_col, right_col = st.columns(2)
    with left_col:
        st.header(":blue[Sales Rep KPIs]")
        st.subheader(f"Total Sales: $ {total_sales:,}")
        st.subheader(f"Payments: $ {total_payments:,}")
        st.subheader(f"Total Orders: {total_orders:,}")
    
    with right_col:
        st.subheader(":blue[Metrics Table]")
        tabular_metrics = df.groupby(["inv_month"], as_index=False).agg({"total_price":"sum","payment_amount":"sum","invoice_number":"count"}).reset_index(drop=True)
        tabular_metrics.columns = ["Month","Sales","Payments","Orders"]
        result_df = tabular_metrics.pivot_table(index=None, values=["Sales","Payments","Orders"], columns="Month",aggfunc="sum")
        st.write(result_df)

    st.markdown("---")

def sales_payments_trend_chart(df):
    order_trend = df.groupby("inv_month")[["invoice_number"]].count()
    sales_payments = df.groupby("inv_month")[["total_price","payment_amount"]].sum()
    sales_payments.columns = ["Sales","Payments"]
    left_col, right_col = st.columns(2)
    with left_col:
        fig_sales_payments = px.line(sales_payments, x=sales_payments.index, y=["Sales","Payments"], title="Total Sales vs Total Payments",line_shape="linear", render_mode="svg",labels={"variable": "Sales vs Payments"})
        fig_sales_payments.update_xaxes(title_text="Month")
        fig_sales_payments.update_yaxes(title_text="Amount")
        fig_sales_payments.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
        st.plotly_chart(fig_sales_payments)

    with right_col:
        fig_invoice_trend = px.bar(order_trend,x=order_trend.index,y="invoice_number",color="invoice_number",labels={"invoice_number":"Order Count"},title="Order Trend")
        fig_invoice_trend.update_xaxes(title_text="Month")
        fig_invoice_trend.update_yaxes(title_text="Quantity")
        st.plotly_chart(fig_invoice_trend)

if __name__ == "__main__":
    select_df = rep_selection()
    rep_kpi_metrics(select_df)
    sales_payments_trend_chart(select_df)
