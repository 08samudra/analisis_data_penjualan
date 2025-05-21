import pandas as pd
import os

# --- 1. Definisikan Lokasi File ---
# Ini adalah path ke folder "datasets" yang berada di level yang sama dengan skrip ini.
datasets_folder = "datasets"

# Ini adalah folder tempat all_data.csv akan disimpan, juga di level yang sama.
output_folder = "dashboard"
output_file_name = "all_data.csv"
output_file_path = os.path.join(output_folder, output_file_name)

# Buat folder output jika belum ada
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# --- 2. Fungsi untuk Memuat dan Menggabungkan Data ---
def create_all_data_csv(datasets_path, final_output_path):
    print(f"Memuat data dari: {datasets_path}")

    try:
        # Memuat semua dataset yang relevan untuk penggabungan
        customers = pd.read_csv(os.path.join(datasets_path, "customers_dataset.csv"))
        order_items = pd.read_csv(os.path.join(datasets_path, "order_items_dataset.csv"))
        order_payments = pd.read_csv(os.path.join(datasets_path, "order_payments_dataset.csv"))
        order_reviews = pd.read_csv(os.path.join(datasets_path, "order_reviews_dataset.csv"))
        orders = pd.read_csv(os.path.join(datasets_path, "orders_dataset.csv"))
        products = pd.read_csv(os.path.join(datasets_path, "products_dataset.csv"))
        sellers = pd.read_csv(os.path.join(datasets_path, "sellers_dataset.csv"))
        product_category_translation = pd.read_csv(os.path.join(datasets_path, "product_category_name_translation.csv"))

    except FileNotFoundError as e:
        print(f"Error: Salah satu file dataset tidak ditemukan. Pastikan path '{datasets_path}' benar dan semua file CSV ada di dalamnya.")
        print(f"Detail error: {e}")
        return

    print("Data berhasil dimuat.")

    # --- 3. Data Cleaning & Preprocessing Awal ---
    # Konversi kolom tanggal di orders_df
    date_columns = [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_columns:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')

    # Filter orders yang sudah delivered
    orders_delivered = orders[orders['order_status'] == 'delivered'].copy()

    # Tangani nilai hilang di product_category_name sebelum merge
    products['product_category_name'] = products['product_category_name'].fillna('unknown_category')

    # Gabungkan terjemahan kategori produk
    products = pd.merge(products, product_category_translation, on='product_category_name', how='left')
    products['product_category_name_cleaned'] = products['product_category_name_english'].fillna(products['product_category_name'])
    products = products.drop(columns=['product_category_name_english', 'product_category_name'])
    products = products.rename(columns={'product_category_name_cleaned': 'product_category_name'})

    # Agregasi review (ambil yang pertama per order_id jika ada duplikat)
    order_reviews_cleaned = order_reviews.drop_duplicates(subset='order_id', keep='first')


    # --- 4. Menggabungkan Dataset ---
    print("Memulai proses penggabungan data...")

    # Gabungkan orders dan order_items
    df_merged = pd.merge(orders_delivered, order_items, on='order_id', how='inner')

    # Gabungkan dengan order_payments
    df_merged = pd.merge(df_merged, order_payments, on='order_id', how='inner')

    # Gabungkan dengan customers
    df_merged = pd.merge(df_merged, customers, on='customer_id', how='inner')

    # Gabungkan dengan products (setelah kategori diterjemahkan)
    df_merged = pd.merge(df_merged, products, on='product_id', how='inner')

    # Gabungkan dengan sellers
    df_merged = pd.merge(df_merged, sellers, on='seller_id', how='inner')

    # Gabungkan dengan order_reviews
    df_merged = pd.merge(df_merged, order_reviews_cleaned, on='order_id', how='left')

    print("Penggabungan data selesai.")

    # --- 5. Final Cleaning (Opsional: Hapus kolom yang tidak relevan) ---
    print(f"Bentuk final dataframe: {df_merged.shape}")
    print("Beberapa baris pertama dari dataframe gabungan:")
    print(df_merged.head())

    # --- 6. Simpan ke CSV ---
    print(f"Menyimpan data gabungan ke: {final_output_path}")
    df_merged.to_csv(final_output_path, index=False)
    print("File all_data.csv berhasil dibuat!")

# --- Jalankan Fungsi Penggabungan ---
create_all_data_csv(datasets_folder, output_file_path)