import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Dashboard KPI Penjualan")

# Load data
# Assuming the data file is uploaded and available in the same directory as app_new.py
try:
    # Use the correct file name based on the previous upload
    data = pd.read_csv('Sales Transaction v.4a.csv')
except FileNotFoundError:
    st.error("Data file 'Sales Transaction v.4a.csv' not found. Please upload the file.")
    st.stop()


# Data Cleaning
data['TotalPrice'] = data['Price'] * data['Quantity']
data = data[data['Quantity'] > 0].copy() # Use .copy() to avoid SettingWithCopyWarning

# Convert 'Date' column to datetime objects
data['Date'] = pd.to_datetime(data['Date'])

# Extract Month and Year
data['MonthYear'] = data['Date'].dt.to_period('M')

# Calculate KPIs

# Rata-rata Nilai Transaksi (ATV)
revenue = data['TotalPrice'].sum()
unique_transactions = data['TransactionNo'].nunique()
atv = revenue / unique_transactions

# Tingkat Pertumbuhan Penjualan Bulanan
monthly_revenue = data.groupby('MonthYear')['TotalPrice'].sum()
monthly_sales_growth = monthly_revenue.pct_change().fillna(0) * 100

# 5 Produk Terlaris
top_5_products = data.groupby('ProductName')['Quantity'].sum().nlargest(5)
total_units_sold = data['Quantity'].sum()
sales_5_best_percentage = (top_5_products.sum() / total_units_sold) * 100

# Tingkat Retensi Pelanggan
# Identify unique customers in each month
customers_per_month = data.groupby('MonthYear')['CustomerNo'].unique().apply(list)

# Calculate retained customers for each month (customers present in current and previous month)
retained_customers = []
for i in range(1, len(customers_per_month)):
    previous_month_customers = set(customers_per_month.iloc[i-1])
    current_month_customers = set(customers_per_month.iloc[i])
    retained_count = len(previous_month_customers.intersection(current_month_customers))
    retained_customers.append(retained_count)

# Calculate total unique customers over time (excluding the first month)
total_unique_customers_after_first_month = len(set().union(*customers_per_month[1:]))

# Avoid division by zero if there are no customers after the first month
if total_unique_customers_after_first_month > 0:
    retention_rate = (sum(retained_customers) / total_unique_customers_after_first_month) * 100
else:
    retention_rate = 0

# Rata-rata Jumlah Item per Transaksi
avg_items_per_transaction = data['Quantity'].sum() / unique_transactions


# Define KPI target values
atv_target = 250000.0
monthly_sales_growth_target = 5.0  # in percentage
top_5_products_sales_target = 15.0 # in percentage
retention_rate_target = 20.0 # in percentage
avg_items_per_transaction_target = 3.0


# Check KPI achievement status
atv_achieved = atv >= atv_target
monthly_sales_growth_achieved = monthly_sales_growth.mean() >= monthly_sales_growth_target
sales_5_best_percentage_achieved = sales_5_best_percentage >= top_5_products_sales_target
retention_rate_achieved = retention_rate >= retention_rate_target
avg_items_per_transaction_achieved = avg_items_per_transaction >= avg_items_per_transaction_target

# Create a DataFrame to display KPIs, targets, and their status
kpi_data = {
    "KPI": ["Rata-rata Nilai Transaksi (ATV)", "Tingkat Pertumbuhan Penjualan Bulanan (rata-rata)",
            "Tingkat Penjualan 5 Produk Terlaris", "Tingkat Retensi Pelanggan",
            "Rata-rata Jumlah Item per Transaksi"],
    "Value": [f"{atv:.2f}", f"{monthly_sales_growth.mean():.2f}%",
              f"{sales_5_best_percentage:.2f}%", f"{retention_rate:.2f}%",
              f"{avg_items_per_transaction:.2f}"],
    "Target": [f"≥ {atv_target:.2f}", f"≥ {monthly_sales_growth_target:.2f}%",
               f"≥ {top_5_products_sales_target:.2f}%", f"≥ {retention_rate_target:.2f}%",
               f"≥ {avg_items_per_transaction_target:.2f}"],
    "Status": ["Achieved ✅" if atv_achieved else "Not Achieved ❌",
               "Achieved ✅" if monthly_sales_growth_achieved else "Not Achieved ❌",
               "Achieved ✅" if sales_5_best_percentage_achieved else "Not Achieved ❌",
               "Achieved ✅" if retention_rate_achieved else "Not Achieved ❌",
               "Achieved ✅" if avg_items_per_transaction_achieved else "Not Achieved ❌"]
}

kpi_df = pd.DataFrame(kpi_data)

st.subheader("Indikator Kinerja Utama (KPI) Status")
st.dataframe(kpi_df)

import matplotlib.pyplot as plt
import seaborn as sns

# Visualize Monthly Revenue
fig_revenue, ax_revenue = plt.subplots(figsize=(12, 6))
monthly_revenue.plot(kind='line', marker='o', ax=ax_revenue)
ax_revenue.set_title('Monthly Revenue')
ax_revenue.set_xlabel('Month-Year')
ax_revenue.set_ylabel('Revenue')
ax_revenue.grid(True)
st.subheader("Monthly Revenue")
st.pyplot(fig_revenue)

# Visualize Monthly Sales Growth Rate
fig_growth, ax_growth = plt.subplots(figsize=(12, 6))
monthly_sales_growth.plot(kind='bar', ax=ax_growth)
ax_growth.set_title('Monthly Sales Growth Rate')
ax_growth.set_xlabel('Month-Year')
ax_growth.set_ylabel('Growth Rate (%)')
ax_growth.grid(axis='y')
st.subheader("Monthly Sales Growth Rate")
st.pyplot(fig_growth)
