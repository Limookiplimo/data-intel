import streamlit as st
import plotly.express as px
from Overview import create_pandas_dataframe
st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align: center; color: green'> ABC Customers</h1>", unsafe_allow_html=True)

def customer_selection():
    df = create_pandas_dataframe()
    customer_df = df.groupby(["crm", "inv_month"], as_index=False)[["total_price", "payment_amount","invoice_number"]].sum()
    customer_choice = customer_df["crm"].unique()
    default_customer = ["CRM001"]

    for cust in default_customer:
        if cust not in customer_choice:
            default_customer.remove(cust)
    crm = st.multiselect("Select Customer: ", options=customer_choice, default=default_customer)
    select_df = df.query("crm == @crm")
    return select_df

def customer_kpi_metrics(df):
    total_sales = int(df["total_price"].sum())
    total_payments = int(df["payment_amount"].sum())
    total_invoices = df["invoice_number"].count()
    left_col, right_col = st.columns(2)
    with left_col:
        st.header(":blue[Customer KPIs]")
        st.subheader(f"Sales: $ {total_sales:,}")
        st.subheader(f"Payments: $ {total_payments:,}")
        st.subheader(f"Invoices: {total_invoices:,}")

    with right_col:
        st.subheader(":blue[Metrics Table]")
        tabular_metrics = df.groupby(["inv_month"], as_index=False).agg({"total_price":"sum","payment_amount":"sum","invoice_number":"count"}).reset_index(drop=True)
        tabular_metrics.columns = ["Month", "Sales", "Payments", "Invoices"]
        result_df = tabular_metrics.pivot_table(index=None, values=["Sales", "Payments", "Invoices"], columns="Month", aggfunc="sum")
        st.write(result_df)

    st.markdown("---")

def customer_purchase_sales_chart(df):
    invoice_trend = df.groupby("inv_month")[["invoice_number"]].count()
    sales_payments = df.groupby("inv_month")[["total_price", "payment_amount"]].sum()
    sales_payments.columns = ["Sales", "Payments"]
    left_col, right_col = st.columns(2)
    with left_col:
        fig_invoice_trend = px.bar(invoice_trend,x=invoice_trend.index,y="invoice_number",color="invoice_number",labels={"invoice_number":"Quantity"},title="Purchase Trend")
        fig_invoice_trend.update_xaxes(title_text="Month")
        st.plotly_chart(fig_invoice_trend)

    with right_col:
        fig_sales_payments = px.line(sales_payments, x=sales_payments.index, y=["Sales", "Payments"], title="Total Sales vs Total Payments",line_shape="linear", render_mode="svg", labels={"variable": "Sales vs Payments"})
        fig_sales_payments.update_xaxes(title_text="Month")
        fig_sales_payments.update_yaxes(title_text="Amount")
        fig_sales_payments.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
        st.plotly_chart(fig_sales_payments)

if __name__ == "__main__":
    select_df = customer_selection()
    customer_kpi_metrics(select_df)
    customer_purchase_sales_chart(select_df)