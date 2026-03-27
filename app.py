import streamlit as st
import pandas as pd
from google.cloud import bigquery

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")

# -------------------- BIGQUERY CONNECTION --------------------
@st.cache_resource
def get_client():
    return bigquery.Client.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

client = get_client()

# -------------------- LOAD RFM DATA --------------------
@st.cache_data
def load_rfm():
    query = """
    SELECT 
        customer_unique_id,
        Recency,
        Frequency,
        Monetary,
        Segment
    FROM `civil-partition-489110-t9.customer_retention.rfm_segmentation`
    """
    return client.query(query).to_dataframe()


# -------------------- LOAD ORDERS DATA --------------------
@st.cache_data
def load_orders():
    query = """
    SELECT 
        customer_unique_id,
        order_id,
        purchase_at,
        total_revenue
    FROM `civil-partition-489110-t9.customer_retention.fact_customer_orders`
    """
    return client.query(query).to_dataframe()


# -------------------- LOAD CUSTOMER BEHAVIOR --------------------
@st.cache_data
def load_behavior():
    query = """
    SELECT 
        customer_unique_id,
        order_id,
        purchase_at,
        customer_type,
        days_since_last_purchase
    FROM `civil-partition-489110-t9.customer_retention.customer_behavior`
    """
    return client.query(query).to_dataframe()


# -------------------- LOAD ALL DATA --------------------
df_rfm = load_rfm()
df_orders = load_orders()
df_behavior = load_behavior()

st.write("RFM:", df_rfm.shape)
st.write("Orders:", df_orders.shape)
st.write("Behavior:", df_behavior.shape)


# -------------------- KPI CALCULATIONS --------------------

total_customers = df_rfm["customer_unique_id"].nunique()

total_orders = df_orders["order_id"].nunique()

total_revenue = df_orders["total_revenue"].sum()

# Repeat Customers %
repeat_customers = df_behavior[df_behavior["customer_type"] == "Repeat"]["customer_unique_id"].nunique()
repeat_rate = (repeat_customers / total_customers) * 100

# Avg Days Between Purchases
avg_days_between = df_behavior["days_since_last_purchase"].dropna().mean()


# -------------------- KPI DISPLAY --------------------

st.subheader("📌 Key Business Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Customers", f"{total_customers:,}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Total Revenue", f"${total_revenue:,.0f}")
col4.metric("Repeat Rate", f"₹{total_revenue:,.0f}")
col5.metric("Avg Days Between Orders", f"{avg_days_between:.1f}")


# -------------------- SEGMENT DISTRIBUTION --------------------

st.subheader("📊 Customer Segmentation")

segment_counts = df_rfm["Segment"].value_counts().reset_index()
segment_counts.columns = ["Segment", "Customers"]

fig_seg = px.bar(
    segment_counts,
    x="Segment",
    y="Customers",
    text="Customers",
    title="Customer Distribution by Segment"
)

st.plotly_chart(fig_seg, use_container_width=True)


# -------------------- REVENUE BY SEGMENT --------------------

rfm_orders = df_orders.merge(df_rfm, on="customer_unique_id", how="left")

revenue_segment = (
    rfm_orders.groupby("Segment")["total_revenue"]
    .sum()
    .reset_index()
    .sort_values(by="total_revenue", ascending=False)
)

fig_rev = px.bar(
    revenue_segment,
    x="Segment",
    y="total_revenue",
    text_auto=True,
    title="Revenue Contribution by Segment"
)

st.plotly_chart(fig_rev, use_container_width=True)

# -------------------- RFM SCATTER --------------------

fig_scatter = px.scatter(
    df_rfm,
    x="Frequency",
    y="Monetary",
    color="Segment",
    size="Monetary",
    hover_data=["customer_unique_id"],
    title="Customer Value Distribution (Frequency vs Monetary)"
)

st.plotly_chart(fig_scatter, use_container_width=True)

# -------------------- RECENCY BY SEGMENT --------------------

recency_segment = (
    df_rfm.groupby("Segment")["Recency"]
    .mean()
    .reset_index()
)

fig_rec = px.bar(
    recency_segment,
    x="Segment",
    y="Recency",
    text_auto=True,
    title="Average Recency by Segment (Lower = Better)"
)

st.plotly_chart(fig_rec, use_container_width=True)


