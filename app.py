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

# 🔹 SIDEBAR FILTERS
# -------------------------------
st.sidebar.header("Filters")

# ✅ Segment Filter (safe check)
if 'Segment' in df.columns:
    segment_filter = st.sidebar.multiselect(
        "Select Segment",
        options=df['Segment'].dropna().unique(),
        default=df['Segment'].dropna().unique()
    )
else:
    segment_filter = None

# ✅ Churn Risk Filter (fix for your KeyError)
if 'Churn_Risk' in df.columns:
    churn_filter = st.sidebar.multiselect(
        "Select Churn Risk",
        options=df['Churn_Risk'].dropna().unique(),
        default=df['Churn_Risk'].dropna().unique()
    )
else:
    st.sidebar.warning("⚠️ 'Churn_Risk' column not found in dataset")
    churn_filter = None

# ✅ Date Range Filter
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])

    date_filter = st.sidebar.date_input(
        "Select Date Range",
        [df['Date'].min(), df['Date'].max()]
    )
else:
    date_filter = None

# ✅ Customer ID Search
if 'Customer_ID' in df.columns:
    customer_search = st.sidebar.text_input("Search Customer ID")
else:
    customer_search = None


# -------------------------------
# 🔹 APPLY FILTERS
# -------------------------------
filtered_df = df.copy()

if segment_filter:
    filtered_df = filtered_df[filtered_df['Segment'].isin(segment_filter)]

if churn_filter:
    filtered_df = filtered_df[filtered_df['Churn_Risk'].isin(churn_filter)]

if date_filter and len(date_filter) == 2:
    filtered_df = filtered_df[
        (filtered_df['Date'] >= pd.to_datetime(date_filter[0])) &
        (filtered_df['Date'] <= pd.to_datetime(date_filter[1]))
    ]

if customer_search:
    filtered_df = filtered_df[
        filtered_df['Customer_ID'].astype(str).str.contains(customer_search)
    ]

# -------------------------------
# 🔹 DEBUG (IMPORTANT)
# -------------------------------
st.write("Filtered Data Preview:", filtered_df.head())
