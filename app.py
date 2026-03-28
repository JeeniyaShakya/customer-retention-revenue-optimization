import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Customer Retention Intelligence System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Understand, Predict, and Act on Customer Behavior</p>", unsafe_allow_html=True)

# -------------------- BIGQUERY --------------------
@st.cache_resource
def get_client():
    return bigquery.Client.from_service_account_info(st.secrets["gcp_service_account"])

client = get_client()

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_rfm():
    return client.query("""
        SELECT customer_unique_id, Recency, Frequency, Monetary, Segment
        FROM `civil-partition-489110-t9.customer_retention.rfm_segmentation`
    """).to_dataframe()

@st.cache_data
def load_orders():
    return client.query("""
        SELECT customer_unique_id, order_id, purchase_at, total_revenue
        FROM `civil-partition-489110-t9.customer_retention.fact_customer_orders`
    """).to_dataframe()

@st.cache_data
def load_behavior():
    return client.query("""
        SELECT customer_unique_id, order_id, purchase_at, customer_type, days_since_last_purchase
        FROM `civil-partition-489110-t9.customer_retention.customer_behavior`
    """).to_dataframe()

@st.cache_data
def load_churn():
    return client.query("""
        SELECT customer_unique_id, recency, frequency, monetary, segment, churn
        FROM `civil-partition-489110-t9.customer_retention.customer_analytics`
    """).to_dataframe()

df_rfm = load_rfm()
df_orders = load_orders()
df_behavior = load_behavior()
df_churn = load_churn()

# -------------------- PREPROCESS --------------------
df_orders["purchase_at"] = pd.to_datetime(df_orders["purchase_at"])
df_behavior["purchase_at"] = pd.to_datetime(df_behavior["purchase_at"])

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🔎 Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df_orders["purchase_at"].min(), df_orders["purchase_at"].max()]
)

selected_segments = st.sidebar.multiselect(
    "Select Segment",
    options=df_rfm["Segment"].unique(),
    default=df_rfm["Segment"].unique()
)

# Apply filters
df_orders = df_orders[
    (df_orders["purchase_at"].dt.date >= date_range[0]) &
    (df_orders["purchase_at"].dt.date <= date_range[1])
]

df_rfm = df_rfm[df_rfm["Segment"].isin(selected_segments)]
df_churn = df_churn[df_churn["segment"].isin(selected_segments)]

# -------------------- KPI SECTION (ALWAYS VISIBLE) --------------------
st.subheader("📌 Key Business Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Customers", f"{total_customers:,}")
col2.metric("Orders", f"{total_orders:,}")
col3.metric("Revenue", f"₹{total_revenue:,.0f}")
col4.metric("Repeat Rate", f"{repeat_rate:.2f}%")
col5.metric("Avg Gap (Days)", f"{avg_days_between:.1f}")

st.divider()

# -------------------- CREATE 2 TABS --------------------
tab1, tab2 = st.tabs(["📊 Customer Overview", "⚠️ Risk & Trends"])

# ==================== TAB 1 ====================
with tab1:

    # ---- Row 1 ----
    col1, col2 = st.columns(2)

    segment_counts = df_rfm["Segment"].value_counts().reset_index()
    segment_counts.columns = ["Segment", "Customers"]

    fig1 = px.bar(segment_counts, x="Segment", y="Customers", text="Customers", height=350)
    col1.plotly_chart(fig1, use_container_width=True)

    rfm_orders = df_orders.merge(df_rfm, on="customer_unique_id")

    revenue_segment = rfm_orders.groupby("Segment")["total_revenue"].sum().reset_index()

    fig2 = px.bar(revenue_segment, x="Segment", y="total_revenue", height=350)
    col2.plotly_chart(fig2, use_container_width=True)

    # ---- Row 2 ----
    col3, col4 = st.columns(2)

    fig3 = px.scatter(df_rfm, x="Frequency", y="Monetary", color="Segment", height=350)
    col3.plotly_chart(fig3, use_container_width=True)

    behavior_counts = df_behavior["customer_type"].value_counts().reset_index()
    behavior_counts.columns = ["Type", "Count"]

    fig4 = px.pie(behavior_counts, names="Type", values="Count", height=350)
    col4.plotly_chart(fig4, use_container_width=True)


# ==================== TAB 2 ====================
with tab2:

    # ---- Fix churn labels ----
    df_churn["churn_label"] = df_churn["churn"].map({
        1: "High Risk",
        0: "Low Risk",
        "High": "High Risk",
        "Low": "Low Risk",
        "Medium": "Medium Risk"
    })

    # ---- Row 1 ----
    col1, col2 = st.columns(2)

    churn_dist = df_churn["churn_label"].value_counts().reset_index()
    churn_dist.columns = ["Churn", "Count"]

    fig1 = px.pie(churn_dist, names="Churn", values="Count", height=350)
    col1.plotly_chart(fig1, use_container_width=True)

    high_risk = df_churn[df_churn["churn_label"] == "High Risk"]

    col2.metric("High Risk Customers", len(high_risk))
    col2.metric("Revenue at Risk", f"₹{high_risk['monetary'].sum():,.0f}")

    # ---- Row 2 ----
    col3, col4 = st.columns(2)

    seg_churn = df_churn.groupby(["segment", "churn_label"]).size().reset_index(name="count")

    fig2 = px.bar(
        seg_churn,
        x="segment",
        y="count",
        color="churn_label",
        height=350
    )
    col3.plotly_chart(fig2, use_container_width=True)

    # Revenue trend
    monthly = df_orders.groupby(df_orders["purchase_at"].dt.to_period("M"))["total_revenue"].sum().reset_index()
    monthly["purchase_at"] = monthly["purchase_at"].astype(str)

    fig3 = px.line(monthly, x="purchase_at", y="total_revenue", height=350)
    col4.plotly_chart(fig3, use_container_width=True)


# -------------------- DEEP DIVE (COMMON BELOW TABS) --------------------
st.divider()
st.subheader("🔍 Customer Deep Dive")

customer_id = st.text_input("Enter Customer ID")

if customer_id:
    rfm_data = df_rfm[df_rfm["customer_unique_id"] == customer_id]
    churn_data = df_churn[df_churn["customer_unique_id"] == customer_id]
    orders_data = df_orders[df_orders["customer_unique_id"] == customer_id]

    if rfm_data.empty:
        st.error("Customer not found")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("Segment", rfm_data["Segment"].values[0])

        churn_val = churn_data["churn_label"].values[0] if not churn_data.empty else "Unknown"
        col2.metric("Churn Risk", churn_val)

        col3.metric("Revenue", f"₹{orders_data['total_revenue'].sum():,.0f}")

        if not orders_data.empty:
            fig = px.line(
                orders_data.sort_values("purchase_at"),
                x="purchase_at",
                y="total_revenue",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
