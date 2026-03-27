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
