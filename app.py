import streamlit as st
import pandas as pd
import plotly.express as px
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

rfm_orders = df_orders.merge(df_rfm, on="customer_unique_id", how="inner")

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

st.subheader("🔁 Customer Behavior Analysis")

col1, col2 = st.columns(2)

# -------------------- NEW vs REPEAT --------------------
behavior_counts = df_behavior["customer_type"].value_counts().reset_index()
behavior_counts.columns = ["customer_type", "count"]

fig_behavior = px.pie(
    behavior_counts,
    names="customer_type",
    values="count",
    title="New vs Repeat Customers"
)

col1.plotly_chart(fig_behavior, use_container_width=True)

# -------------------- DAYS BETWEEN PURCHASES --------------------
df_gap = df_behavior.dropna(subset=["days_since_last_purchase"])

fig_gap = px.histogram(
    df_gap,
    x="days_since_last_purchase",
    nbins=50,
    title="Days Between Purchases Distribution"
)

col2.plotly_chart(fig_gap, use_container_width=True)

st.markdown("### ⏳ Purchase Frequency by Customer Type")

avg_gap = (
    df_behavior.dropna(subset=["days_since_last_purchase"])
    .groupby("customer_type")["days_since_last_purchase"]
    .mean()
    .reset_index()
)

fig_avg_gap = px.bar(
    avg_gap,
    x="customer_type",
    y="days_since_last_purchase",
    title="Average Days Between Purchases (New vs Repeat)",
    text_auto=True
)

st.plotly_chart(fig_avg_gap, use_container_width=True)

st.markdown("### 📅 Orders Over Time")

orders_timeline = (
    df_behavior.groupby(df_behavior["purchase_at"].dt.date)
    .size()
    .reset_index(name="orders")
)

fig_time = px.line(
    orders_timeline,
    x="purchase_at",
    y="orders",
    title="Orders Trend Over Time"
)

st.plotly_chart(fig_time, use_container_width=True)

@st.cache_data
def load_churn():
    query = """
    SELECT 
        customer_unique_id,
        recency,
        frequency,
        monetary,
        segment,
        churn
    FROM `civil-partition-489110-t9.customer_retention.customer_analytics`
    """
    return client.query(query).to_dataframe()

df_churn = load_churn()

st.subheader("⚠️ Churn Risk Analysis")

col1, col2 = st.columns(2)

# -------------------- CHURN DISTRIBUTION --------------------
churn_dist = df_churn["churn"].value_counts().reset_index()
churn_dist.columns = ["churn", "count"]

fig_churn = px.pie(
    churn_dist,
    names="churn",
    values="count",
    title="Customer Churn Distribution"
)

col1.plotly_chart(fig_churn, use_container_width=True)

# -------------------- KPIs --------------------
high_risk_customers = df_churn[df_churn["churn"] == "High"].shape[0]

revenue_at_risk = df_churn[df_churn["churn"] == "High"]["monetary"].sum()

total_customers = df_churn.shape[0]

risk_percent = (high_risk_customers / total_customers) * 100

col2.metric("High Risk Customers", f"{high_risk_customers:,}")
col2.metric("Revenue at Risk", f"₹{revenue_at_risk:,.0f}")
col2.metric("Risk %", f"{risk_percent:.2f}%")

st.markdown("### 📊 Segment vs Churn")

seg_churn = (
    df_churn.groupby(["segment", "churn"])
    .size()
    .reset_index(name="count")
)

fig_seg_churn = px.bar(
    seg_churn,
    x="segment",
    y="count",
    color="churn",
    barmode="group",
    title="Churn Risk Across Segments"
)

st.plotly_chart(fig_seg_churn, use_container_width=True)

st.markdown("### 💰 Revenue at Risk by Segment")

risk_seg = (
    df_churn[df_churn["churn"] == "High"]
    .groupby("segment")["monetary"]
    .sum()
    .reset_index()
)

fig_risk_seg = px.bar(
    risk_seg,
    x="segment",
    y="monetary",
    title="Revenue at Risk (High Churn Customers)"
)

st.plotly_chart(fig_risk_seg, use_container_width=True)

df_orders["purchase_at"] = pd.to_datetime(df_orders["purchase_at"])

st.subheader("📈 Revenue Trend & Forecast")

# -------------------- MONTHLY REVENUE --------------------
monthly_revenue = (
    df_orders
    .groupby(df_orders["purchase_at"].dt.to_period("M"))
    ["total_revenue"]
    .sum()
    .reset_index()
)

monthly_revenue["purchase_at"] = monthly_revenue["purchase_at"].astype(str)


fig_rev = px.line(
    monthly_revenue,
    x="purchase_at",
    y="total_revenue",
    title="Monthly Revenue Trend"
)

st.plotly_chart(fig_rev, use_container_width=True)

# -------------------- FORECAST --------------------
monthly_revenue["revenue_ma"] = (
    monthly_revenue["total_revenue"]
    .rolling(window=3)
    .mean()
)

# Last 3 months avg → forecast
last_ma = monthly_revenue["revenue_ma"].iloc[-1]

# Create future months
last_date = pd.to_datetime(monthly_revenue["purchase_at"].iloc[-1])

future_months = pd.date_range(
    start=last_date,
    periods=4,
    freq="M"
)[1:]

forecast_df = pd.DataFrame({
    "purchase_at": future_months.astype(str),
    "total_revenue": [last_ma] * 3
})

# Label data
monthly_revenue["type"] = "Actual"
forecast_df["type"] = "Forecast"

combined = pd.concat([monthly_revenue, forecast_df])

fig_forecast = px.line(
    combined,
    x="purchase_at",
    y="total_revenue",
    color="type",
    title="Revenue Forecast (Next 3 Months)"
)

st.plotly_chart(fig_forecast, use_container_width=True)


st.subheader("🔍 Customer Deep Dive")

customer_id = st.text_input("Enter Customer Unique ID")

if customer_id:

    # RFM data
    rfm_data = df_rfm[df_rfm["customer_unique_id"] == customer_id]

    # Churn data
    churn_data = df_churn[df_churn["customer_unique_id"] == customer_id]

    # Orders data
    orders_data = df_orders[df_orders["customer_unique_id"] == customer_id]

    # Behavior data
    behavior_data = df_behavior[df_behavior["customer_unique_id"] == customer_id]

    if rfm_data.empty:
        st.error("Customer not found")
    else:

                segment = rfm_data["Segment"].values[0]

        churn = churn_data["churn"].values[0] if not churn_data.empty else "Unknown"

        total_revenue = orders_data["total_revenue"].sum()

        total_orders = orders_data.shape[0]

        avg_gap = behavior_data["days_since_last_purchase"].mean()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Segment", segment)
        col2.metric("Churn Risk", churn)
        col3.metric("Total Revenue", f"₹{total_revenue:,.0f}")
        col4.metric("Total Orders", total_orders)

        st.markdown("### 📊 Behavior Insight")

        st.write(f"Average Days Between Purchases: {avg_gap:.2f}")

        st.markdown("### 💡 Recommendation")

        if churn == "High" and "High Value" in segment:
            st.error("🚨 High-value customer at risk → Offer discounts or loyalty perks immediately")

        elif churn == "High":
            st.warning("⚠️ Customer likely to churn → Send re-engagement campaigns")

        elif churn == "Medium":
            st.info("ℹ️ Monitor customer → Provide personalized offers")

        elif churn == "Low" and "High Value" in segment:
            st.success("✅ Loyal high-value customer → Reward & retain")

        else:
            st.write("Maintain engagement")

        st.markdown("### 📅 Purchase History")

        if not orders_data.empty:
            fig_cust = px.line(
                orders_data.sort_values("purchase_at"),
                x="purchase_at",
                y="total_revenue",
                title="Customer Purchase Timeline"
            )

            st.plotly_chart(fig_cust, use_container_width=True)

