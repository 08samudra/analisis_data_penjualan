# 📊 Proyek Analisis Penjualan ✨

Dashboard interaktif ini dibuat untuk menganalisis data penjualan e-commerce. Dirancang agar mudah dijalankan di **Visual Studio Code** dengan **Python** dan **Streamlit**.

---

## 🔧 Setup Environment (VS Code)

Ikuti langkah-langkah berikut untuk menyiapkan dan menjalankan proyek ini secara lokal di VS Code.

### 1. Kloning Repositori

Buka terminal di VS Code (Terminal > New Terminal atau `Ctrl + Shift + ``), lalu jalankan:

```bash
git clone https://github.com/08samudra/analisis_data_penjualan.git
````

Buka folder proyek:

```bash
cd analisis_data_penjualan
```

---

### 2. Buat dan Aktifkan Virtual Environment

**Windows (PowerShell):**

```bash
python -m venv .venv
.venv\Scripts\activate
```

Jika muncul masalah terkait *Execution Policy*, jalankan PowerShell sebagai Administrator lalu ketik:

```powershell
Set-ExecutionPolicy RemoteSigned
```

Lalu tekan `Y`, dan coba aktivasi ulang.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> Setelah aktivasi berhasil, terminal Anda akan menampilkan `(.venv)` di awal baris.

---

### 3. Instal Dependensi

Pastikan virtual environment sudah aktif, lalu jalankan:

```bash
pip install pandas matplotlib seaborn streamlit
```

---

### 4. Siapkan Data Gabungan (`all_data.csv`)

Di direktori utama proyek, jalankan skrip berikut:

```bash
python create_all_data.py
```

File `all_data.csv` akan otomatis dibuat di dalam folder `dashboard/`.

---

## 🚀 Jalankan Aplikasi Streamlit

Pindah ke direktori `dashboard/`:

```bash
cd dashboard
```

Jalankan aplikasi:

```bash
streamlit run main.py
```

Aplikasi akan terbuka di browser pada alamat: [http://localhost:8501](http://localhost:8501)

---

## ✅ Fitur Interaktif

* Input angka di sidebar untuk menyesuaikan **ambang batas persentase**
* Visualisasi data penjualan secara **interaktif**
---
