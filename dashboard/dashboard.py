import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur gaya visualisasi menggunakan seaborn
sns.set(style='whitegrid')

# Fungsi untuk menghitung total peminjaman per jam
def get_total_count_by_hour_df(hour_df):
    hour_count_df = hour_df.groupby(by="hours").agg({"count_cr": ["sum"]})
    return hour_count_df

# Fungsi untuk mendapatkan data berdasarkan hari untuk tahun 2011
def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query('dteday >= "2011-01-01" and dteday < "2012-12-31"')
    return day_df_count_2011

# Fungsi untuk menghitung total jumlah pengguna yang terdaftar per hari
def total_registered_df(day_df):
    reg_df = day_df.groupby(by="dteday").agg({"registered": "sum"})
    reg_df = reg_df.reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

# Fungsi untuk menghitung total pengguna yang tidak terdaftar per hari
def total_casual_df(day_df):
    cas_df = day_df.groupby(by="dteday").agg({"casual": ["sum"]})
    cas_df = cas_df.reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

# Fungsi untuk menghitung total peminjaman per jam
def sum_order(hour_df):
    sum_order_items_df = hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# Fungsi untuk menghitung peminjaman berdasarkan musim
def macem_season(day_df): 
    season_df = day_df.groupby(by="season").count_cr.sum().reset_index()
    return season_df

# Membaca dataset yang telah dibersihkan
days_df = pd.read_csv("day_clean.csv")
hours_df = pd.read_csv("hour_clean.csv")

# Menetapkan urutan dan reset index pada kolom datetime
datetime_columns = ["dteday"]
days_df.sort_values(by="dteday", inplace=True)
days_df.reset_index(inplace=True)

hours_df.sort_values(by="dteday", inplace=True)
hours_df.reset_index(inplace=True)

# Mengubah kolom dteday menjadi format datetime
for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

# Mendapatkan nilai minimum dan maksimum dari kolom dteday
min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

min_date_hour = hours_df["dteday"].min()
max_date_hour = hours_df["dteday"].max()

# Input tanggal dari Streamlit sidebar
with st.sidebar:
    # Menampilkan logo perusahaan
    st.image("logo.png")
    
    # Mengambil input rentang tanggal dari pengguna
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])

# Memfilter data sesuai dengan rentang waktu yang dipilih
main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & 
                       (days_df["dteday"] <= str(end_date))]

main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) & 
                        (hours_df["dteday"] <= str(end_date))]

# Mendapatkan data hasil pemrosesan untuk visualisasi
hour_count_df = get_total_count_by_hour_df(main_df_hour)
day_df_count_2011 = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = macem_season(main_df_hour)

# Menampilkan header untuk dashboard
st.title('Dashboard Analisis Penyewaan Sepeda')

# Menampilkan metrik untuk data peminjaman harian
st.subheader('Metrik Peminjaman Harian')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_orders = day_df_count_2011.count_cr.sum()
    st.metric("Total Peminjaman Sepeda", value=total_orders)

with col2:
    total_sum = reg_df.register_sum.sum()
    st.metric("Total User Registered", value=total_sum)

with col3:
    total_sum = cas_df.casual_sum.sum()
    st.metric("Total User Casual", value=total_sum)

# Visualisasi performa penjualan dalam bentuk grafik garis
st.subheader("Performa Penjualan Sepeda Sepanjang Waktu")
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    days_df["dteday"],
    days_df["count_cr"],
    marker='o', 
    linewidth=3,
    color="#0288D1"
)
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# Visualisasi jam penyewaan terbanyak dan tersedikit
st.subheader("Jam Peminjaman Paling Banyak dan Paling Sedikit")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 10))

# Menampilkan grafik untuk jam dengan penyewa terbanyak
sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.head(5), palette=["#B0BEC5", "#B0BEC5", "#0288D1", "#B0BEC5", "#B0BEC5"], ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jam (PM)", fontsize=20)
ax[0].set_title("Jam dengan Banyak Penyewa Sepeda", fontsize=24)
ax[0].tick_params(axis='y', labelsize=16)
ax[0].tick_params(axis='x', labelsize=16)
 
# Menampilkan grafik untuk jam dengan penyewa paling sedikit
sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.sort_values(by="hours", ascending=True).head(5), palette=["#B0BEC5", "#B0BEC5", "#B0BEC5", "#B0BEC5","#0288D1"], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jam (AM)", fontsize=20)
ax[1].set_title("Jam dengan Sedikit Penyewa Sepeda", fontsize=24)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=16)
ax[1].tick_params(axis='x', labelsize=16)
 
st.pyplot(fig)

# Visualisasi berdasarkan musim
st.subheader("Peminjaman Sepeda Berdasarkan Musim")
colors = ["#B0BEC5", "#B0BEC5", "#B0BEC5", "#0288D1"]
fig, ax = plt.subplots(figsize=(18, 8))
sns.barplot(
        y="count_cr", 
        x="season",
        data=season_df.sort_values(by="season", ascending=False),
        palette=colors,
        ax=ax
    )
ax.set_title("Grafik Peminjaman Sepeda Berdasarkan Musim", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel("Musim", fontsize=20)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=16)
st.pyplot(fig)

# Visualisasi perbandingan pelanggan yang terdaftar dan casual
st.subheader("Perbandingan Customer Registered dan Casual")
labels = 'Casual', 'Registered'
sizes = [18.8, 81.2]
explode = (0, 0.1) 

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', colors=["#B0BEC5", "#0288D1"],
        shadow=True, startangle=90)
ax1.axis('equal')  

st.pyplot(fig1)
