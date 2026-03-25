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
