# 📊 Dashboard ABM Risiko Kredit Mikro UMKM

Dashboard modern untuk final project mata kuliah **Pemodelan dan Simulasi Data C**. Aplikasi menggunakan **Streamlit** untuk menampilkan simulasi **Agent-Based Modeling (ABM)** risiko kredit mikro UMKM dengan tampilan UI/UX premium.

## 👤 Identitas

- **Nama:** Ahmad Hamdan Hamidiy
- **Email:** hamdanhamidiy2687@webmail.ac.id
- **Topik:** Simulasi ABM Risiko Kredit Mikro UMKM

## ✨ Fitur Dashboard

### 📌 Ringkasan
- Metric cards dengan glassmorphism design
- Gauge chart default rate terbaik & terburuk
- Radar chart perbandingan antar skenario
- Interpretasi otomatis hasil simulasi

### 🏪 Dataset UMKM
- Filter interaktif: sektor, range skor kredit, range pinjaman
- Heatmap korelasi antar variabel numerik
- Distribusi skor kredit dan risiko per sektor
- Download dataset ke CSV

### 📈 Simulasi What-If
- Area chart default rate, risiko, profit, dan stressor
- Stacked area chart agen aktif vs default
- Heatmap default rate per bulan per skenario
- 4 skenario bawaan + 1 skenario custom

### 🎲 Monte Carlo
- Histogram distribusi + violin plot
- Convergence plot rata-rata kumulatif
- Scatter plot default rate vs profit
- Statistik lengkap (mean, median, std, min, max)
- Analisis sensitivitas kekuatan intervensi

### 🧠 Formulasi Model
- Flowchart visual alur proses simulasi
- Formula transisi risiko dengan penjelasan variabel
- Peta kesesuaian dengan ketentuan tugas

### ❓ Panduan & Bantuan
- Cara membaca dashboard step-by-step
- Glosarium istilah (12+ istilah)
- FAQ interaktif
- Referensi akademik

## 🎨 Desain
- Dark glassmorphism theme
- Animated gradient hero section
- Google Font Inter
- Hover effects & fade-in animations
- Responsive layout

## 📁 Struktur Folder

```text
streamlit_abm_umkm_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── data/
│   └── dataset_umkm_dummy.csv
└── src/
    ├── __init__.py
    ├── data_generator.py
    ├── simulation.py
    └── styles.py
```

## 🚀 Cara Menjalankan di Laptop

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Cara Deploy ke Streamlit Community Cloud

1. Upload semua file project ini ke repository GitHub public.
2. Buka [Streamlit Community Cloud](https://share.streamlit.io).
3. Pilih **New app**.
4. Pilih repository GitHub yang sudah dibuat.
5. Pada bagian **Main file path**, isi: `app.py`
6. Klik **Deploy**.

## 📝 Catatan Presentasi

Pada presentasi, jelaskan bahwa agen adalah pelaku UMKM. Setiap agen memiliki skor kredit, risiko awal, kerentanan, resiliensi, beban pinjaman, dan status default. Risiko agen berubah setiap bulan akibat stressor ekonomi, intervensi, dan efek penularan risiko sektor. Output utama dashboard adalah default rate, approval rate, risiko rata-rata, dan profit portofolio kredit.
