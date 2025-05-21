import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(
    page_title="Dashboard Analisis Penjualan",
    page_icon="📊",
    layout="wide"
)

# --- Fungsi untuk Memuat Data ---
@st.cache_data
def load_data():
    all_data_path = "../dashboard/all_data.csv"

    if not os.path.exists(all_data_path):
        st.error(f"Error: File '{all_data_path}' tidak ditemukan.")
        st.info("Pastikan Anda sudah menjalankan skrip penggabungan data (create_all_data.py) dan all_data.csv ada di lokasi yang benar.")
        st.stop()
        
    try:
        df = pd.read_csv(all_data_path)
        return df
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat all_data.csv: {e}")
        st.stop()

# --- Fungsi untuk Data Cleaning dan Merging ---
@st.cache_data
def clean_and_merge_data(df_raw):
    
    date_columns = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date',
        'review_creation_date',
        'review_answer_timestamp'
    ]
    for col in date_columns:
        if col in df_raw.columns:
            df_raw[col] = pd.to_datetime(df_raw[col], errors='coerce')

    df_cleaned = df_raw[df_raw['order_status'] == 'delivered'].copy()

    # --- PERBAIKAN DI SINI UNTUK FORMATTING ---

    # 1. Format Nama Kota (customer_city)
    if 'customer_city' in df_cleaned.columns:
        # Ubah semua huruf menjadi huruf kecil, lalu kapital setiap kata
        df_cleaned['customer_city'] = df_cleaned['customer_city'].str.lower().str.title()
        # Koreksi khusus untuk "Sao Paulo"
        df_cleaned['customer_city'] = df_cleaned['customer_city'].replace('Sao Paulo', 'São Paulo')
        # Tambahkan koreksi lain jika ada (contoh: "Rio De Janeiro" menjadi "Rio de Janeiro")
        df_cleaned['customer_city'] = df_cleaned['customer_city'].replace('Rio De Janeiro', 'Rio de Janeiro')


    # 2. Format Nama Kategori Produk (product_category_name)
    if 'product_category_name' in df_cleaned.columns:
        # Ganti underscore dengan spasi, lalu kapital setiap kata
        df_cleaned['product_category_name'] = df_cleaned['product_category_name'].str.replace('_', ' ').str.title()
        # Tangani nilai hilang (jika ada setelah formatting)
        df_cleaned['product_category_name'] = df_cleaned['product_category_name'].fillna('Unknown Category')


    # Tangani nilai hilang numerik yang mungkin ada
    numeric_cols_to_check = [
        'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm',
        'product_name_lenght', 'product_description_lenght', 'product_photos_qty',
        'price', 'freight_value', 'payment_value', 'review_score'
    ]
    for col in numeric_cols_to_check:
        if col in df_cleaned.columns and df_cleaned[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
            else:
                df_cleaned[col] = df_cleaned[col].fillna('missing')

    columns_to_keep = [
        'order_id', 'customer_id', 'product_id', 'customer_city',
        'customer_state', 'price', 'freight_value', 'payment_value',
        'product_category_name',
        'seller_id',
        'review_score',
        'order_purchase_timestamp'
    ]
    df_selected = df_cleaned[[col for col in columns_to_keep if col in df_cleaned.columns]].copy()

    df_selected = df_selected.dropna(subset=['customer_city', 'product_category_name', 'payment_value']).copy()
    
    df_selected.drop_duplicates(subset=['order_id', 'product_id', 'customer_id'], inplace=True)

    return df_selected

# --- Memuat dan Membersihkan Data ---
df_raw = load_data()
df_cleaned = clean_and_merge_data(df_raw)

# --- Sidebar untuk Kontrol Interaktif ---
st.sidebar.header("Pengaturan Ambang Batas")

threshold_city = st.sidebar.number_input(
    "Ambang Batas Kontribusi Kota (%)",
    min_value=0.01,
    max_value=100.00,
    value=10.00,
    step=0.01,
    format="%.2f"
)

threshold_product = st.sidebar.number_input(
    "Ambang Batas Kontribusi Produk (%)",
    min_value=0.01,
    max_value=100.00,
    value=50.00,
    step=0.01,
    format="%.2f"
)

st.sidebar.info("Anda bisa mengetik langsung nilai persentase atau menggunakan tombol +/- untuk mengatur ambang batas.")

# --- Bagian Dashboard Utama ---
st.title("📊 Dashboard Analisis Penjualan")
st.markdown("Dashboard ini menyajikan analisis kota dengan penjualan tertinggi dan produk dominan di kota tersebut, dengan ambang batas yang dapat disesuaikan.")

# --- 1. Analisis Kota dengan Penjualan Tertinggi ---
st.header(f"1. Kota dengan Penjualan Tertinggi (Kontribusi >= {threshold_city:.2f}%)")
st.write(f"Menganalisis kota mana yang menghasilkan nilai penjualan tertinggi dan menyumbang setidaknya **{threshold_city:.2f}%** dari total nilai transaksi penjualan secara keseluruhan.")

city_sales = df_cleaned.groupby('customer_city')['payment_value'].sum().reset_index()
city_sales = city_sales.sort_values(by='payment_value', ascending=False)

total_overall_sales = df_cleaned['payment_value'].sum()

city_sales['contribution_percentage'] = (city_sales['payment_value'] / total_overall_sales) * 100

st.subheader("Top 10 Kota Berdasarkan Nilai Penjualan")
st.dataframe(city_sales.head(10).style.format({"payment_value": "R$ {:,.2f}", "contribution_percentage": "{:.2f}%"}))

top_contributing_cities = city_sales[city_sales['contribution_percentage'] >= threshold_city]

if not top_contributing_cities.empty:
    dominant_city = top_contributing_cities.iloc[0]['customer_city']
    st.success(f"**🎉  Kota dominan yang menyumbang setidaknya {threshold_city:.2f}% dari total penjualan adalah: :blue[{dominant_city}]**")
    st.dataframe(top_contributing_cities.style.format({"payment_value": "R$ {:,.2f}", "contribution_percentage": "{:.2f}%"}))
else:
    st.warning(f"Tidak ada satu pun kota yang secara individual menyumbang setidaknya {threshold_city:.2f}% dari total penjualan. Menampilkan kota dengan penjualan tertinggi sebagai 'kota dominan' untuk analisis produk.")
    dominant_city = city_sales.iloc[0]['customer_city']
    st.info(f"Kota dominan yang akan dianalisis produknya adalah: :blue[{dominant_city}]")

st.subheader("Visualisasi Penjualan Kota Teratas")
fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.barplot(x='customer_city', y='payment_value', data=city_sales.head(10), hue='customer_city', palette='viridis', ax=ax1, legend=False)
ax1.set_title('Top 10 Kota Berdasarkan Nilai Penjualan')
ax1.set_xlabel('Kota Pelanggan')
ax1.set_ylabel('Total Nilai Penjualan (R$)')
ax1.ticklabel_format(style='plain', axis='y')
plt.xticks(rotation=45, ha='right')
st.pyplot(fig1)

st.subheader("Kontribusi Penjualan Kumulatif per Kota")
fig2, ax2 = plt.subplots(figsize=(12, 6))
city_sales['cumulative_contribution'] = city_sales['contribution_percentage'].cumsum()
sns.lineplot(x=range(len(city_sales)), y='cumulative_contribution', data=city_sales, ax=ax2)
ax2.axhline(y=threshold_city, color='r', linestyle='--', label=f'{threshold_city:.2f}% Threshold')
ax2.set_title('Kontribusi Penjualan Kumulatif per Kota (Diurutkan)')
ax2.set_xlabel('Peringkat Kota')
ax2.set_ylabel('Kontribusi Kumulatif (%)')
ax2.grid(True)
ax2.legend()
st.pyplot(fig2)


# --- 2. Analisis Produk Dominan di Kota Terpilih ---
st.header(f"2. Produk Dominan di Kota :blue[{dominant_city}] (Kontribusi >= {threshold_product:.2f}%)")
st.write(f"Menganalisis kategori produk yang paling dominan di **{dominant_city}**, yaitu yang menyumbang minimal **{threshold_product:.2f}%** dari total nilai transaksi penjualan di kota tersebut.")

df_dominant_city = df_cleaned[df_cleaned['customer_city'] == dominant_city].copy()

if df_dominant_city.empty:
    st.error(f"Data transaksi untuk kota '{dominant_city}' tidak ditemukan atau terlalu sedikit untuk analisis produk. Mohon pilih ambang batas kota yang memungkinkan.")
else:
    product_sales_in_dominant_city = df_dominant_city.groupby('product_category_name')['payment_value'].sum().reset_index()
    product_sales_in_dominant_city = product_sales_in_dominant_city.sort_values(by='payment_value', ascending=False)

    total_sales_in_dominant_city = df_dominant_city['payment_value'].sum()

    product_sales_in_dominant_city['contribution_percentage'] = \
        (product_sales_in_dominant_city['payment_value'] / total_sales_in_dominant_city) * 100

    st.subheader(f"Top 10 Kategori Produk Berdasarkan Nilai Penjualan di {dominant_city}")
    st.dataframe(product_sales_in_dominant_city.head(10).style.format({"payment_value": "R$ {:,.2f}", "contribution_percentage": "{:.2f}%"}))

    dominant_products_in_city = product_sales_in_dominant_city[
        product_sales_in_dominant_city['contribution_percentage'] >= threshold_product
    ]

    if not dominant_products_in_city.empty:
        st.success(f"**🎉 Kategori produk yang menyumbang setidaknya {threshold_product:.2f}% dari total penjualan di {dominant_city} adalah:**")
        st.dataframe(dominant_products_in_city.style.format({"payment_value": "R$ {:,.2f}", "contribution_percentage": "{:.2f}%"}))
    else:
        st.info(f"Tidak ada satu pun kategori produk yang secara individual menyumbang setidaknya {threshold_product:.2f}% dari total penjualan di '{dominant_city}'.")

    st.subheader("Visualisasi Kontribusi Produk di Kota Dominan")
    fig3, ax3 = plt.subplots(figsize=(14, 7))
    sns.barplot(x='product_category_name', y='contribution_percentage',
                data=product_sales_in_dominant_city.head(10), hue='product_category_name', palette='magma', ax=ax3, legend=False)
    ax3.set_title(f'Top 10 Kategori Produk Berdasarkan Kontribusi Penjualan di {dominant_city}')
    ax3.set_xlabel('Kategori Produk')
    ax3.set_ylabel('Persentase Kontribusi (%)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig3)

st.markdown("---")
st.caption("Copyright (C) Yoga Samudra 2025")