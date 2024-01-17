import streamlit as st
import plotly.express as px
from Overview import create_pandas_dataframe
st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align: center; color: green'> Trading Routes</h1>", unsafe_allow_html=True)

def sales_per_route_chart():
    df = create_pandas_dataframe()
    total_customers = df["crm"].count()
    estimated_value = 150000000
    total_sales = int(df["total_price"].sum())
    route_sales_monthly = df.groupby(["route","inv_month"],as_index=False)["total_price"].sum()
    left_chart, right_chart = st.columns(2)
    with left_chart:
        st.header(":blue[Route KPIs]", divider="gray")
        st.subheader(f"Route Value: $ {estimated_value:,}")

        st.subheader(f"Total Sales: $ {total_sales:,}")

        st.subheader(f"Total Shops: {total_customers:,}")

    with right_chart:
        fig_monthly_sales = px.line(route_sales_monthly, x="inv_month", y="total_price", title="Monthly Sales", color="route", line_shape="linear", render_mode="svg")
        st.plotly_chart(fig_monthly_sales)

def monthly_sales_and_top_customers_chart():
    df = create_pandas_dataframe()
    route_sales = df.groupby("route")[["total_price"]].sum()
    top_customers = df.groupby("crm")[["total_price"]].sum().nlargest(10, "total_price")
    left_chart, right_chart = st.columns(2)
    with left_chart:
        fig_total_sales = px.bar(route_sales,x=route_sales.index,y="total_price",color='total_price',labels={'total_price':'Total Sales'},title="Trading Routes")
        fig_total_sales.update_xaxes(title_text="Route")
        st.plotly_chart(fig_total_sales)
    with right_chart:
        fig_top_customers = px.bar(top_customers,x=top_customers.index,y="total_price",color="total_price",labels={"total_price": "Total Sales"},title="Top Customers")
        fig_top_customers.update_xaxes(title_text="Customer")
        st.plotly_chart(fig_top_customers)
    st.markdown("---")

if __name__ == "__main__":
    sales_per_route_chart()
    monthly_sales_and_top_customers_chart()


