import streamlit as st
import pandas as pd
from google.cloud import bigquery
import plotly.express as px

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")

st.title("📊 Customer Retention Intelligence System")

# -------------------- BIGQUERY CONNECTION --------------------
client = bigquery.Client.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# -------------------- LOAD DATA --------------------
query = """
SELECT *
FROM `civil-partition-489110-t9.customer_retention.churn_prediction`
"""

@st.cache_data
def load_data():
    df = client.query(query).to_dataframe()

    st.write(df.columns)
df.columns = df.columns.str.strip().str.replace(" ", "_")

# Create Churn_Risk if missing
if 'Churn_Risk' not in df.columns:
    if 'Churn' in df.columns:
        df['Churn_Risk'] = df['Churn'].apply(lambda x: "High" if x == 1 else "Low")
    
    return df

df = load_data()

# -------------------- OVERVIEW --------------------
st.subheader("📊 Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", df['customer_unique_id'].nunique())
col2.metric("Total Revenue", round(df['Monetary'].sum(), 2))
col3.metric("Avg Revenue", round(df['Monetary'].mean(), 2))

# -------------------- RFM CALCULATION --------------------

# R Score (Recency: lower is better)
df['r_score'] = pd.qcut(df['Recency'], 4, labels=[4, 3, 2, 1], duplicates='drop')

# F Score (Frequency: higher is better)
df['f_score'] = pd.qcut(df['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4], duplicates='drop')

# M Score (Monetary: higher is better)
df['m_score'] = pd.qcut(df['Monetary'], 4, labels=[1, 2, 3, 4], duplicates='drop')

# Combine RFM
df['rfm_score'] = df['r_score'].astype(str) + df['f_score'].astype(str) + df['m_score'].astype(str)

# -------------------- SEGMENTATION --------------------
def segment_customer(row):
    if row['m_score'] == 4 and row['r_score'] >= 3:
        return "High Value Recent"
    elif row['m_score'] == 4 and row['r_score'] <= 2:
        return "At Risk High Value"
    elif row['f_score'] == 1:
        return "Low Value / One-time"
    else:
        return "Others"

df['segment'] = df.apply(segment_customer, axis=1)

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🔍 Filters")

segment_filter = st.sidebar.multiselect(
    "Select Segment",
    options=df['segment'].dropna().unique(),
    default=df['segment'].dropna().unique()
)

# ✅ FIXED COLUMN NAME: Churn_Risk
churn_filter = st.sidebar.multiselect(
    "Churn Risk",
    options=df['Churn_Risk'].dropna().unique(),
    default=df['Churn_Risk'].dropna().unique()
)

# -------------------- FILTER DATA --------------------
filtered_df = df[
    (df['segment'].isin(segment_filter)) &
    (df['Churn_Risk'].isin(churn_filter))
]

# -------------------- VISUALS --------------------

# Customer Segmentation
st.subheader("📊 Customer Segmentation")
segment_counts = filtered_df['segment'].value_counts()
st.bar_chart(segment_counts)

# Churn Distribution
st.subheader("⚠️ Churn Risk Distribution")
churn_counts = filtered_df['Churn_Risk'].value_counts()
st.bar_chart(churn_counts)

# Revenue by Segment
st.subheader("💰 Revenue by Segment")
revenue_segment = filtered_df.groupby('segment')['Monetary'].sum()
st.bar_chart(revenue_segment)

# -------------------- TREND ANALYSIS --------------------
query2 = """
SELECT *
FROM `civil-partition-489110-t9.customer_retention.monthly_orders`
"""

@st.cache_data
def load_trend():
    df_trend = client.query(query2).to_dataframe()
    
    # Clean column names
    df_trend.columns = df_trend.columns.str.strip().str.replace(" ", "_")
    
    df_trend['Month'] = pd.to_datetime(df_trend['Month'])
    
    return df_trend

df_trend = load_trend()

st.subheader("📈 Order Trend Over Time")
st.line_chart(df_trend.set_index('Month')['Total_Orders'])

# -------------------- INSIGHTS --------------------
st.subheader("🧠 Key Insights")

st.write("""
- Majority of customers are low frequency → retention opportunity
- High-value customers contribute most revenue
- Customers with high recency are more likely to churn
- Target 'At Risk High Value' segment for retention campaigns
""")

# -------------------- ADVANCED VISUAL (PLOTLY) --------------------
fig = px.bar(
    segment_counts,
    title="Customer Segments Distribution",
    labels={'value': 'Count', 'index': 'Segment'}
)

st.plotly_chart(fig, use_container_width=True)
