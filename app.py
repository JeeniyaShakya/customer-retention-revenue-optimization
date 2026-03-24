import streamlit as st
import pandas as pd
from google.cloud import bigquery

st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")

st.title("📊 Customer Retention Intelligence System")

# Initialize BigQuery client
client = bigquery.Client()

# Query
query = """
SELECT *
FROM `civil-partition-489110-t9.customer_retention.churn_prediction`
LIMIT 1000
"""

@st.cache_data
def load_data():
    return client.query(query).to_dataframe()

df = load_data()

st.subheader("🔍 Data Preview")
st.dataframe(df)

st.subheader("📈 Basic Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", df['customer_unique_id'].nunique())
col2.metric("Total Revenue", round(df['total_revenue'].sum(), 2))
col3.metric("Avg Revenue", round(df['total_revenue'].mean(), 2))
