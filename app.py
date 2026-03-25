import streamlit as st
import pandas as pd
from google.cloud import bigquery

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

st.write("Columns in dataset:", df.columns)

st.subheader("📊 Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", df['customer_unique_id'].nunique())

# 👉 Replace with correct column after checking
col2.metric("Total Revenue", round(df['total_revenue'].sum(), 2))

col3.metric("Avg Revenue", round(df['total_revenue'].mean(), 2))
