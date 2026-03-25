import streamlit as st
import pandas as pd
from google.cloud import bigquery

st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")

st.title("📊 Customer Retention Intelligence System")

client = bigquery.Client.from_service_account_info(
    st.secrets["gcp_service_account"]
)

query = """
SELECT *
FROM `civil-partition-489110-t9.customer_retention.churn_prediction`
"""

@st.cache_data
def load_data():
    return client.query(query).to_dataframe()

df = load_data()

st.subheader("📊 Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", df['customer_unique_id'].nunique())
col2.metric("Total Revenue", round(df['Monetary'].sum(), 2))
col3.metric("Avg Revenue", round(df['Monetary'].mean(), 2))

st.sidebar.header("🔍 Filters")

# R Score (Recency: lower is better)
df['r_score'] = pd.qcut(df['Recency'], 4, labels=[4,3,2,1])

# F Score (Frequency: higher is better)
df['f_score'] = pd.qcut(df['Frequency'].rank(method='first'), 4, labels=[1,2,3,4])

# M Score (Monetary: higher is better)
df['m_score'] = pd.qcut(df['Monetary'], 4, labels=[1,2,3,4])


df['rfm_score'] = df['r_score'].astype(str) + df['f_score'].astype(str) + df['m_score'].astype(str)

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

segment_filter = st.sidebar.multiselect(
    "Select Segment",
    options=df['segment'].unique(),
    default=df['segment'].unique()
)


churn_filter = st.sidebar.multiselect(
    "Churn Risk",
    options=df['Churn Risk'].unique(),
    default=df['Churn Risk'].unique()
)

filtered_df = df[
    (df['segment'].isin(segment_filter)) &
    (df['Churn Risk'].isin(churn_filter))
]

st.subheader("📊 Customer Segmentation")

segment_counts = filtered_df['segment'].value_counts()

st.bar_chart(segment_counts)

st.subheader("⚠️ Churn Risk Distribution")

churn_counts = filtered_df['Churn Risk'].value_counts()

st.bar_chart(churn_counts)

st.subheader("💰 Revenue by Segment")

revenue_segment = filtered_df.groupby('Segment')['Monetary'].sum()

st.bar_chart(revenue_segment)

query2 = """
SELECT *
FROM `civil-partition-489110-t9.customer_retention.monthly_orders`
"""

df_trend = client.query(query2).to_dataframe()

df_trend['Month'] = pd.to_datetime(df_trend['Month'])

st.subheader("📈 Order Trend Over Time")

st.line_chart(df_trend.set_index('Month')['Total_Orders'])

st.subheader("🧠 Key Insights")

st.write("""
- Majority of customers are low frequency → retention opportunity
- High-value customers contribute most revenue
- Customers with high recency are more likely to churn
- Target 'At Risk' segment for retention campaigns
""")

import plotly.express as px

fig = px.bar(segment_counts, title="Customer Segments")
st.plotly_chart(fig, use_container_width=True)
