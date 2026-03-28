# 🚀 Customer Retention Intelligence System

---

## 📌 Problem Statement

Most businesses don’t lose customers instantly — they lose them gradually over time.  
However, identifying early churn signals and understanding customer behavior is difficult without a structured data system.

This project addresses this by:
- Detecting churn risk early  
- Understanding customer purchase patterns  
- Identifying revenue-driving segments  
- Supporting data-driven retention strategies  

---

## 🎯 Goal / Purpose

The goal of this project is to build an end-to-end system that:

- Tracks customer lifecycle and behavior  
- Segments customers using RFM analysis  
- Predicts churn probability  
- Helps businesses optimize revenue and retention strategies  

---

## 📊 Key Visuals (Dashboard)

The Streamlit dashboard includes:

- Total Customers (KPI)  
- Total Revenue (KPI)  
- Average Revenue per Customer  
- Customer Segmentation (RFM-based)  
- Churn Probability Distribution  
- Revenue Trends over time  

---

## 📈 Business Impact / Insights

- A large portion of customers are **one-time buyers**, indicating retention opportunities  
- Revenue is concentrated among a **small group of high-value customers**  
- High-risk customers with high revenue contribution were identified  
- Churn prediction enables proactive engagement strategies  
- Helps businesses prioritize marketing efforts effectively  

---

## 📸 Dashboard Screenshots

![Dashboard Screenshot 1](https://github.com/JeeniyaShakya/customer-retention-revenue-optimization/blob/main/Screenshot%202026-03-25%20095021.png)  
![Dashboard Screenshot 2](https://github.com/JeeniyaShakya/customer-retention-revenue-optimization/blob/main/Screenshot%202026-03-25%20095035.png)  

---

## 🌐 Live Application

👉 [Click here to view the live app](https://customer-retention-revenue-optimization-n54x9exdh8bdqvtlkd2v8e.streamlit.app/)

---

## ⚙️ Techniques Used

### 🔹 Data Engineering (dbt)
- Data cleaning using staging models  
- Fact table creation for transactions  
- Mart layer for customer analytics  
- SQL window functions:
  - ROW_NUMBER()
  - LAG()
  - MIN() OVER()

---

### 🔹 Analytics & Machine Learning (Python)

#### RFM Segmentation
- Recency: Days since last purchase  
- Frequency: Number of orders  
- Monetary: Total revenue  

#### Churn Prediction
- Logistic Regression model  
- Predicts probability of customer churn  

---

## 🧱 Tech Stack

- BigQuery  
- dbt  
- Python (Pandas, Scikit-learn)  
- Streamlit  
