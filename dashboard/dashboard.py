import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set seaborn theme to darkgrid and use monochrome color palette
sns.set(style='darkgrid', palette='gray')

# Helper functions

def create_daily_orders_df(df):
    df['date'] = pd.to_datetime(df['date'])
    orders_df = df.resample('M', on='date').sum()
    return orders_df

def create_sum_casual_user_df(df):
    sum_casual_user_df = df.groupby("day").casual_user.sum().sort_values(ascending=False).reset_index()
    return sum_casual_user_df

def create_sum_registered_user_df(df):
    sum_registered_user_df = df.groupby("day").registered_user.sum().sort_values(ascending=False).reset_index()
    return sum_registered_user_df

def create_byweather_df(df):
    byweather_df = df.groupby("weather").total_user.sum().sort_values(ascending=False).reset_index()
    return byweather_df

def create_byseason_df(df):
    byseason_df = df.groupby("season").total_user.sum().sort_values(ascending=False).reset_index()
    return byseason_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="day", as_index=False).agg({
        "date": "max",
        "instant": "nunique",
        "total_user": "sum"
    })
    rfm_df.columns = ["day", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

# Prepare dataframe
day_df = pd.read_csv("dashboard/day_clean.csv")

# Ensure the date column are of type datetime
datetime_columns = ["date"]
day_df.sort_values(by="date", inplace=True)
day_df.reset_index(inplace=True)
for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])

# Create filter components
min_date = day_df["date"].min()
max_date = day_df["date"].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Range of Time', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_df[(day_df["date"] >= str(start_date)) & 
                 (day_df["date"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_casual_user_df = create_sum_casual_user_df(main_df)
sum_registered_user_df = create_sum_registered_user_df(main_df)
byweather_df = create_byweather_df(main_df)
byseason_df = create_byseason_df(main_df)
rfm_df = create_rfm_df(main_df)

# Create dashboard
st.header('Bike Dashboard :sparkles:')

# Plot Bike Sharing Productivity by Month
st.subheader('Bike Sharing Productivity by Month')
fig, ax = plt.subplots(figsize=(20,5))
sns.pointplot(data=main_df, x='month', y='total_user', errorbar=None, ax=ax)
ax.set(title='Bike Sharing Productivity by Month', ylabel='Total User', xlabel='Month')
st.pyplot(fig)

# Number of Users by Weather and Season
st.subheader("Number of Users by Weather and Season")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(y="total_user", x="weather", data=byweather_df.sort_values(by="total_user", ascending=False), palette=colors, hue="weather", legend=False, ax=ax[0])
ax[0].set_title("Number of User by Weather", fontsize=15)
ax[0].ticklabel_format(style='plain', axis='y')

sns.barplot(y="total_user", x="season", data=byseason_df.sort_values(by="total_user", ascending=False), palette=colors, hue="season", legend=False, ax=ax[1])
ax[1].set_title("Number of User by Season", fontsize=15)
ax[1].ticklabel_format(style='plain', axis='y')

plt.suptitle("Number of Users by Weather and Season", fontsize=20)
st.pyplot(fig)

# RFM Analysis
st.subheader("Best Customer Based on RFM Parameters (day)")
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="day", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, hue="day", legend=False, ax=ax[0])
ax[0].set_title("By Recency (days)", fontsize=18)

sns.barplot(y="frequency", x="day", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, hue="day", legend=False, ax=ax[1])
ax[1].set_title("By Frequency", fontsize=18)

sns.barplot(y="monetary", x="day", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, hue="day", legend=False, ax=ax[2])
ax[2].set_title("By Monetary", fontsize=18)

plt.suptitle("Best Customer Based on RFM Parameters (day)", fontsize=20)
st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center;">'
    'Copyright © 2024 All Rights Reserved '
    '<a href="https://www.linkedin.com/in/firdania-sasmita-sari-9587b5305/">Firdania Sasmita Sari</a>'
    '</div>', unsafe_allow_html=True
)
