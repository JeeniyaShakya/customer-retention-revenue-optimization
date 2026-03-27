import streamlit as st
from google.cloud import bigquery

# Initialize client
client = bigquery.Client()

# -------------------------------
# Load RFM Table
# -------------------------------
@st.cache_data
def load_rfm():
    query = """
    SELECT 
        customer_id,
        recency,
        frequency,
        monetary,
        rfm_segment
    FROM `your_project.your_dataset.rfm_table`
    """
    return client.query(query).to_dataframe()

# -------------------------------
# Load Orders Table
# -------------------------------
@st.cache_data
def load_orders():
    query = """
    SELECT 
        order_id,
        customer_id,
        order_date,
        order_value
    FROM `your_project.your_dataset.orders_table`
    """
    return client.query(query).to_dataframe()

# -------------------------------
# Load Behavior Table
# -------------------------------
@st.cache_data
def load_behavior():
    query = """
    SELECT 
        customer_id,
        order_id,
        product_category,
        warehouse_id,
        order_hour
    FROM `your_project.your_dataset.behavior_table`
    """
    return client.query(query).to_dataframe()


# -------------------------------
# Call functions
# -------------------------------
rfm_df = load_rfm()
orders_df = load_orders()
behavior_df = load_behavior()

# Debug prints (optional)
st.write("RFM:", rfm_df.shape)
st.write("Orders:", orders_df.shape)
st.write("Behavior:", behavior_df.shape)
