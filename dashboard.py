import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go
import plotly.express as px
from branca.element import MacroElement
from jinja2 import Template
from folium import Element

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Prevalensi Stunting", page_icon="📊", layout="wide")

# CSS Style
#st.markdown("""<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""", unsafe_allow_html=True)

# Set title
# Judul dengan background color dan style cantik menggunakan HTML dan CSS
st.markdown("""
    <div style="
        background-color: #FFFFFF; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 10px solid #1E3A8A; 
        border-right: 10px solid #1E3A8A;
        border-color: #1E3A8A; 
        box-shadow: 3px 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;">
        <h1 style="color: #1E3A8A; font-family: Arial, sans-serif; margin: 0; font-size: 32px;">
            Dashboard Prevalensi Stunting di Indonesia
        </h1>
    </div>
""", unsafe_allow_html=True)

# Informasi tambahan
st.info("Visualisasi Data Prevalensi Stunting berdasarkan Indeks Khusus Penanganan Stunting")

# Style metric cards
style_metric_cards(
    background_color="#FFFFFF",
    border_left_color="#2A9DF4",
    border_color="#FFFFFF",
    box_shadow="#F71938"
)

# Load dataset utama
file_path = "C:/Users/Asus/OneDrive/Kuliah/SKRIPSI/Model/sebaranstunting.csv"
df = pd.read_csv(file_path)

# Sidebar untuk filter (bisa dibiarkan sebagai sidebar minimal)
st.sidebar.header("Filter Data")

year_options = ["All"] + sorted(df["Tahun"].unique())
selected_year = st.sidebar.multiselect(
    "Pilih Tahun:",
    options=year_options
)

province_options = ["All"] + sorted(df["Provinsi"].unique())
selected_province = st.sidebar.multiselect(
    "Pilih Provinsi:",
    options=province_options
)

# Menentukan kabupaten yang tersedia berdasarkan provinsi yang dipilih
if "All" not in selected_province:
    filtered_provinces = df[df["Provinsi"].isin(selected_province)]["Kab/Kota"].unique()
else:
    filtered_provinces = df["Kab/Kota"].unique()

# Pilihan Kabupaten/Kota dengan opsi 'All' dan kabupaten yang sesuai dengan provinsi yang dipilih
city_options = ["All"] + sorted(filtered_provinces)
selected_city = st.sidebar.multiselect(
    "Pilih Kabupaten/Kota:",
    options=city_options
)

# Filter data berdasarkan pilihan
if "All" in selected_year:
    selected_year = df["Tahun"].unique()

if "All" in selected_province:
    selected_province = df["Provinsi"].unique()

if "All" in selected_city:
    selected_city = df["Kab/Kota"].unique()

# Filter data berdasarkan inputan yang telah dipilih
filtered_data = df.query(
    "`Tahun` in @selected_year & `Provinsi` in @selected_province & `Kab/Kota` in @selected_city"
)

# Pastikan data tidak memiliki nilai null di latitude atau longitude
filtered_data = filtered_data.dropna(subset=['Latitude', 'Longitude'])

# Fungsi utama halaman
def HomePage():
    # Membuat expander untuk informasi
    with st.expander("🌐 Informasi"):
        st.write("""
        Berikut keterangan rentang nilai prevalensi dan IKPS
        
        **Prevalensi**
        - Baik: < 10%
        - Menengah: 10% - 20%
        - Buruk: > 20%
        
        **IKPS**
        - Optimal: > 75%
        - Stabil: 50% - 75%
        - Rendah: < 50%


        Berikut adalah informasi tentang analisis klasterisasi data stunting
    
        **Tahun 2020**
        - Klaster 1 🟢: Prevalensi Baik, IKPS Optimal
        - Klaster 0 🟠: Prevalensi Menengah, IKPS Stabil
        - Klaster 2 🔴: Prevalensi Buruk, IKPS Rendah
    
        **Tahun 2021**
        - Klaster 1 🟢: Prevalensi Menengah, IKPS Optimal
        - Klaster 2 🟠: Prevalensi Buruk, IKPS Stabil
        - Klaster 0 🔴: Prevalensi Baik, IKPS Rendah

        **Tahun 2022**
        - Klaster 0 🟢: Prevalensi Menengah, IKPS Optimal
        - Klaster 2 🟠: Prevalensi Buruk, IKPS Stabil
        - Klaster 1 🔴: Prevalensi Baik, IKPS Rendah
        """)
    
    with st.expander("🏨 Data Tabel"):
        shwdata = st.multiselect('Kolom yang Ingin Ditampilkan:', filtered_data.columns, default=[])
        st.dataframe(filtered_data[shwdata] if shwdata else filtered_data, use_container_width=True)

    # Statistik
    total_balita = int(filtered_data['Jumlah Balita'].sum())
    total_stunting = int(filtered_data['Jumlah Stunting'].sum())
    avg_prevalensi = round(filtered_data['Prevalensi'].mean(), 2)
    avg_ikps = round(filtered_data['IKPS'].mean(), 2)
    clusters = filtered_data['Klaster'].value_counts().to_dict()

    total1, total2, total3, total4, total5 = st.columns(5, gap='large')
    with total1:
        st.info('Jumlah Balita', icon="👶")
        st.metric(label='Total', value=f"{total_balita:,}")

    with total2:
        st.info('Jumlah Stunting', icon="🔻")
        st.metric(label='Total', value=f"{total_stunting:,}")

    with total3:
        st.info('Prevalensi', icon="📊")
        st.metric(label='Rata-rata (%)', value=f"{avg_prevalensi}%")

    with total4:
        st.info('IKPS', icon="📈")
        st.metric(label='Rata-rata', value=f"{avg_ikps}")

    with total5:
        st.info('Klaster', icon="🔄")
        for cluster, count in clusters.items():
            st.write(f"Klaster {cluster}: {count} wilayah")
    style_metric_cards(
        background_color="#FFFFFF", border_left_color="#2A9DF4", border_color="#FFFFFF", box_shadow="#F71938"
    )

    # Layout untuk peta dan tabel ranking
    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
        
        # Definisikan warna dan deskripsi klaster berdasarkan tahun
        cluster_settings = {
            2020: { 0: ('orange', 'Prevalensi Menengah, IKPS Stabil'),
                    1: ('green', 'Prevalensi Baik, IKPS Optimal'),
                    2: ('red', 'Prevalensi Buruk, IKPS Rendah')},
            2021: { 0: ('red', 'Prevalensi Baik, IKPS Rendah'),
                    1: ('green', 'Prevalensi Menengah, IKPS Optimal'),
                    2: ('orange', 'Prevalensi Buruk, IKPS Stabil')},
            2022: { 0: ('green', 'Prevalensi Menengah, IKPS Optimal'),
                    1: ('red', 'Prevalensi Baik, IKPS Rendah'),
                    2: ('orange', 'Prevalensi Buruk, IKPS Stabil')}
        }

        # Peta Folium
        st.info('**Peta Distribusi dan Klasterisasi Stunting**')
        # Tambahkan deskripsi di bawah st.info
        st.markdown(
            """
            <div style="font-size: 12px; line-height: 1.5;">
                🟢 <b>Prevalensi Rendah (baik)</b>, Indikator Terpenuhi<br>
                🟠 <b>Prevalensi (Rendah-Tinggi) Sedang</b>, Penanganan Indikator belum Maksimal<br>
                🔴 <b>Prevalensi Tinggi</b>, Indikator Rendah
            </div>
            """,
            unsafe_allow_html=True
        )

        m = folium.Map(location=[-2.5, 118], zoom_start=5, tiles='cartodbpositron')
        marker_cluster = MarkerCluster().add_to(m)

        # Iterasi data dengan logika warna dan deskripsi per tahun
        for _, row in filtered_data.iterrows():
            tahun = row['Tahun']
            klaster = row['Klaster']
            jumlah_balita_stunting = row['Jumlah Stunting']
            ikps = row['IKPS']
            
            # Perhitungan balita tertangani dan belum tertangani
            balita_tertangani = (ikps * jumlah_balita_stunting) / 100
            balita_belum_tertangani = jumlah_balita_stunting - balita_tertangani

            # Format nilai sebagai bilangan bulat untuk tampilan
            balita_tertangani = int(balita_tertangani)
            balita_belum_tertangani = int(balita_belum_tertangani)
    
            # Ambil warna dan deskripsi dari pengaturan klaster berdasarkan tahun
            color, description = cluster_settings.get(tahun, {}).get(klaster, ('gray', 'Tidak ada data deskripsi'))
    
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(
                    f"""
                    <div style="width: 300px; font-size: 12px; line-height: 1.4;">
                        <b>{row['Kab/Kota']}</b><br>
                        <b>Tahun:</b> {tahun}<br>
                        <b>Prevalensi:</b> {row['Prevalensi']}%<br>
                        <b>IKPS:</b> {row['IKPS']}%<br>
                        <b>Balita Tertangani:</b> {balita_tertangani}<br>
                        <b>Balita Belum Tertangani:</b> {balita_belum_tertangani}<br>
                        <b>Klaster:</b> {klaster}<br>
                        <b>Deskripsi:</b> {description}
                    </div>
                    """,
                    max_width=350),
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(marker_cluster)

            folium.Circle(
                location=[row['Latitude'], row['Longitude']],
                radius=5000,
                color=color,
                fill=True,
                fill_opacity=0.5,
                popup=folium.Popup(
                    f"""
                    <div style="width: 300px; font-size: 12px; line-height: 1.4;">
                        <b>{row['Kab/Kota']}</b><br>
                        <b>Tahun:</b> {tahun}<br>
                        <b>Klaster:</b> {klaster} ({description})
                    </div>
                    """,
                    max_width=350)
            ).add_to(m)
        
        # Render peta di Streamlit
        folium_static(m)

    with col2:
        # Tabel Ranking
        st.info('**Ranking Wilayah Prioritas**')

        # Ranking wilayah berdasarkan prevalensi tinggi dan IKPS rendah
        ranked_data = filtered_data.sort_values(by=['Prevalensi', 'IKPS'], ascending=[False, True])
        ranked_data = ranked_data[['Tahun','Kab/Kota', 'Prevalensi', 'IKPS', 'Klaster']].reset_index(drop=True)
        ranked_data.index += 1
        
        # Format angka desimal menjadi hanya 1 angka di belakang koma
        ranked_data['Prevalensi'] = ranked_data['Prevalensi'].map(lambda x: f"{x:.1f}")
        ranked_data['IKPS'] = ranked_data['IKPS'].map(lambda x: f"{x:.1f}")

        # Styling untuk baris pertama
        def highlight_top_rows(row):
            if row.name == 1:
                return ['background-color: #FF5733; color: white; font-weight: bold'] * len(row)
            else:
                return ['background-color: #F0F8FF; color: black'] * len(row)

        # Menampilkan tabel dengan styling
        st.dataframe(
            ranked_data.style.apply(highlight_top_rows, axis=1)
            .set_table_styles([
                {'selector': 'th', 'props': [('font-size', '12px'), ('color', '#4B4B4B'), ('font-weight', 'bold')]},
                {'selector': 'td', 'props': [('font-size', '12px')]},
                {'selector': 'tr:hover', 'props': [('background-color', '#D6EAF8')]}  # Hover effect
            ]),
            height=560,  # Menentukan tinggi tabel
            use_container_width=True
        )
    style_metric_cards(
        background_color="#FFFFFF",
        border_left_color="#2A9DF4",
        border_color="#FFFFFF",
        box_shadow="#F71938"
    )
    

    # Layout untuk 2 kolom
    grafik1, grafik2 = st.columns([1, 2], gap="large")

    with grafik1:
        st.info('**Perbandingan Prevalensi dan IKPS**')
        # Grouping data, memastikan Tahun tetap utuh sebagai index
        comparison_df = filtered_data.groupby('Tahun', as_index=False)[['Prevalensi', 'IKPS']].mean()

        # Pastikan Tahun tetap berupa integer (jika perlu)
        comparison_df['Tahun'] = comparison_df['Tahun'].astype(int)

        # Plot garis
        st.line_chart(comparison_df.set_index('Tahun'))
    
    with grafik2:
        st.info('**Rata-rata per Indikator**')
        # Pilih indikator 
        indikator_cols = [
            'Imunisasi', 'Penolong Persalinan..',
            'KB Modern', 'ASI Eksklusif', 'MP ASI', 'Air Minum Layak', 'Sanitasi Layak',
            'PAUD', 'Kepemilikan JKN/jamkesda', 'Penerima Bantuan Pangan']  
    
        # Filter data untuk indikator saja dan hitung rata-rata
        indikator_avg = filtered_data[indikator_cols].mean().sort_values(ascending=True)

        # Plot bar chart menggunakan Plotly Express
        fig = px.bar(
            x=indikator_avg.values,
            y=indikator_avg.index,
            orientation='h',
            labels={'x': 'Rata-rata (%)', 'y': 'Indikator'},
            color=indikator_avg.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    # Menambahkan kesimpulan analisis

    # Mengecek jika input wilayah lebih dari satu atau hanya satu
    if len(selected_city) > 1:  # Jika inputan lebih dari satu wilayah
        # Filter data untuk analisis
        wilayah_prevalensi_tinggi = filtered_data.loc[filtered_data['Prevalensi'].idxmax()]
        nama_wilayah = wilayah_prevalensi_tinggi['Kab/Kota']
        prevalensi_tertinggi = wilayah_prevalensi_tinggi['Prevalensi']
        indikator_terendah = indikator_avg.idxmin()  # Indikator dengan nilai terendah rata-rata

        st.info(
            f"Berdasarkan analisis, wilayah yang paling rentan dengan prevalensi tertinggi adalah **{nama_wilayah}** "
            f"dengan prevalensi sebesar **{prevalensi_tertinggi:.2f}%**. Indikator yang paling rendah di wilayah tersebut "
            f"adalah **{indikator_terendah}**, sehingga perlu menjadi fokus utama untuk peningkatan."
        )

    elif len(selected_city) == 1:  # Jika inputan hanya satu wilayah
        # Filter data untuk wilayah tunggal
        data_wilayah = filtered_data[filtered_data['Kab/Kota'] == selected_city[0]].iloc[0]
        nama_wilayah = data_wilayah['Kab/Kota']
        prevalensi = data_wilayah['Prevalensi']
        klaster = data_wilayah['Klaster']
        indikator_terendah = indikator_avg.idxmin()  # Indikator dengan nilai terendah rata-rata

        st.info(
            f"Kabupaten **{nama_wilayah}** memiliki prevalensi sebesar **{prevalensi:.2f}%** dan berada pada klaster **{klaster}**. "
            f"Penanganan yang perlu ditingkatkan adalah pada indikator **{indikator_terendah}**."
        )

    else:  # Jika tidak ada inputan
        st.warning("Silakan pilih setidaknya satu wilayah untuk melihat hasil analisis.")

    
# Menjalankan HomePage secara langsung
HomePage()
