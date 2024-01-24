import streamlit as st
import plotly.express as px
from Overview import create_pandas_dataframe

st.set_page_config(layout="wide")
st.markdown("<h2 style='text-align: center; color: green'> ABC Logistics</h1>", unsafe_allow_html=True)

def logistics_kpis():
    df = create_pandas_dataframe()
    logistics_df = df.groupby(["vehicle"],as_index=False).agg({"total_weight":"sum","invoice_number":"count"})
    logistics_df.columns = ["Vehicle","Weight","Deliveries"]

    total_tonnes = int(logistics_df["Weight"].sum())
    total_deliveries = logistics_df["Deliveries"].sum()
    left_col, right_col = st.columns(2)
    with left_col:
        st.header(":blue[Logistics KPIs]")
        st.subheader(f"Total Tonnes: $ {total_tonnes:,}t")
        st.subheader(f"Total Deliveries: {total_deliveries:,}")
    with right_col:
        st.subheader(":blue[Metrics Table]")
        metrics_df = logistics_df.pivot_table(index=None, values=["Weight", "Deliveries"], columns="Vehicle", aggfunc="sum")
        st.write(metrics_df)

    st.markdown("---")

def logistics_charts():
    df = create_pandas_dataframe()
    tonnage_month = df.groupby("pmt_month")[["total_weight"]].sum()
    tonnage_vehicle = df.groupby(["vehicle", "pmt_month"], as_index=False)["total_weight"].sum()
    tonnage_vehicle.columns = ["Vehicles","Month","Weight"]
    left_col, right_col = st.columns(2)
    with left_col:
        fig_monthly_tonnage = px.bar(tonnage_month,x=tonnage_month.index,y="total_weight", color="total_weight",labels={"total_weight":"Weight"},title="Tonnes Per Month")
        fig_monthly_tonnage.update_xaxes(title_text="Month")
        st.plotly_chart(fig_monthly_tonnage)

    with right_col:
        fig_vehicle_tonnage = px.line(tonnage_vehicle, x="Month",y="Weight", title="Tonnes Per Vehicle", color="Vehicles", line_shape="linear", render_mode="svg")
        st.plotly_chart(fig_vehicle_tonnage)

if __name__=="__main__":
    logistics_kpis()
    logistics_charts()

    