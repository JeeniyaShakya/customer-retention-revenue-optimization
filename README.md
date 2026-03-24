# 🚀 Customer Retention & Revenue Optimization System

## 📌 Overview
This project builds an end-to-end data pipeline to analyze customer behavior, identify churn risk, and optimize revenue using **BigQuery, dbt, and Python**.

It simulates a real-world product analytics system used by companies to:
- Understand customer lifecycle
- Identify high-value and at-risk customers
- Predict churn probability
- Drive data-driven retention strategies

---

## 🎯 Problem Statement
Most companies do not lose customers suddenly — they lose them gradually.

This project aims to:
- Identify churn risk early  
- Segment customers based on behavior  
- Analyze revenue contribution  
- Enable targeted retention strategies  

---

## 🧱 Tech Stack

- **Data Warehouse:** BigQuery  
- **Transformation Tool:** dbt  
- **Analytics & ML:** Python (Pandas, Scikit-learn)  
- **Visualization (Optional):** Power BI / Streamlit  

---

## ⚙️ Data Modeling (dbt)

### 🔹 Staging Layer
- Cleaned and standardized raw datasets  
- Converted timestamps and renamed columns  

### 🔹 Fact Table
**fact_customer_orders**
- Combined orders, customers, and revenue  
- One row per order  

### 🔹 Mart Layer
**mart_customer_retention**
- Customer lifecycle metrics  
- First purchase, repeat behavior  
- Days between purchases  

---

## 📊 Analytics Layer (Python)

### 🔹 RFM Segmentation
- **Recency:** Days since last purchase  
- **Frequency:** Number of orders  
- **Monetary:** Total revenue  

Customers classified into:
- Champions  
- Loyal  
- At Risk  
- Lost  

---

### 🔹 Churn Prediction
- Built using Logistic Regression  
- Features used:
  - Recency  
  - Frequency  
  - Monetary  

Output:
- Probability of churn for each customer  

---

## 🔁 Data Write-back

Final analytics results were pushed back into BigQuery using:

```python
to_gbq(
    churn_df,
    "customer_retention.churn_prediction",
    project_id="your_project_id",
    if_exists="replace"
)

