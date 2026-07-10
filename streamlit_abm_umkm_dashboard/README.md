# Dashboard ABM Risiko Kredit Mikro UMKM

Dashboard ini dibuat untuk final project mata kuliah **Pemodelan dan Simulasi Data C**. Aplikasi menggunakan **Streamlit** untuk menampilkan simulasi **Agent-Based Modeling (ABM)** risiko kredit mikro UMKM.

## Identitas

- Nama: Ahmad Hamdan Hamidiy
- Email: hamdanhamidiy2687@webmail.ac.id
- Topik: Simulasi ABM Risiko Kredit Mikro UMKM

## Fitur Dashboard

1. Dataset dummy UMKM otomatis.
2. Simulasi Agent-Based Modeling berbasis agen UMKM.
3. Empat skenario what-if:
   - Baseline
   - Guncangan Ekonomi
   - Intervensi KUR
   - Seleksi Kredit Ketat
4. Monte Carlo hingga 1000 iterasi.
5. Grafik default rate, rata-rata risiko, estimasi profit, distribusi Monte Carlo, dan analisis sensitivitas.
6. Tampilan UI/UX modern dengan sidebar, card metrik, tab analisis, dan grafik interaktif Plotly.

## Struktur Folder

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

## Cara Menjalankan di Laptop

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cara Deploy ke Streamlit Community Cloud

1. Upload semua file project ini ke repository GitHub public.
2. Buka Streamlit Community Cloud.
3. Pilih **New app**.
4. Pilih repository GitHub yang sudah dibuat.
5. Pada bagian **Main file path**, isi:

```text
app.py
```

6. Klik **Deploy**.

## Catatan Presentasi

Pada presentasi, jelaskan bahwa agen adalah pelaku UMKM. Setiap agen memiliki skor kredit, risiko awal, kerentanan, resiliensi, beban pinjaman, dan status default. Risiko agen berubah setiap bulan akibat stressor ekonomi, intervensi, dan efek penularan risiko sektor. Output utama dashboard adalah default rate, approval rate, risiko rata-rata, dan profit portofolio kredit.
