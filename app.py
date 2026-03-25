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

segment_filter = st.sidebar.multiselect(
    "Select Segment",
    options=df['Segment'].unique(),
    default=df['Segment'].unique()
)

churn_filter = st.sidebar.multiselect(
    "Churn Risk",
    options=df['Churn Risk'].unique(),
    default=df['Churn Risk'].unique()
)

filtered_df = df[
    (df['Segment'].isin(segment_filter)) &
    (df['Churn Risk'].isin(churn_filter))
]

st.subheader("📊 Customer Segmentation")

segment_counts = filtered_df['Segment'].value_counts()

st.bar_chart(segment_counts)
