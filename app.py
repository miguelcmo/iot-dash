import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IoT Dashboard", layout="wide")

st.title("📡 IoT Monitoring Dashboard")

# =============================
# CARGA DE DATOS
# =============================
uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    
    # Limpieza básica
    df.columns = df.columns.str.strip()
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    return df

if uploaded_file:
    df = load_data(uploaded_file)

    st.sidebar.header("🔎 Filtros")

    # =============================
    # FILTROS
    # =============================
    devices = st.sidebar.multiselect(
        "Seleccionar dispositivos",
        df['device_id'].unique(),
        default=df['device_id'].unique()
    )

    status_filter = st.sidebar.multiselect(
        "Estado",
        df['status'].unique(),
        default=df['status'].unique()
    )

    df_filtered = df[
        (df['device_id'].isin(devices)) &
        (df['status'].isin(status_filter))
    ]

    # =============================
    # KPIs
    # =============================
    st.subheader("📊 Métricas clave")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🌡 Temp Promedio", f"{df_filtered['temperature'].mean():.2f} °C")
    col2.metric("💧 Humedad Promedio", f"{df_filtered['humidity'].mean():.2f} %")
    col3.metric("⚡ Energía Promedio", f"{df_filtered['energy_consumption'].mean():.2f}")
    col4.metric("⚠️ Fallos", df_filtered[df_filtered['status'] == 'FAIL'].shape[0])

    # =============================
    # SERIES DE TIEMPO
    # =============================
    st.subheader("📈 Series de tiempo")

    tab1, tab2, tab3 = st.tabs(["Temperatura", "Humedad", "Energía"])

    with tab1:
        fig = px.line(df_filtered, x="timestamp", y="temperature", color="device_id")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.line(df_filtered, x="timestamp", y="humidity", color="device_id")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = px.line(df_filtered, x="timestamp", y="energy_consumption", color="device_id")
        st.plotly_chart(fig, use_container_width=True)

    # =============================
    # ANÁLISIS POR DISPOSITIVO
    # =============================
    st.subheader("📦 Análisis por dispositivo")

    device_group = df_filtered.groupby("device_id").mean(numeric_only=True).reset_index()

    fig = px.bar(device_group, x="device_id", y="temperature", title="Temperatura promedio por dispositivo")
    st.plotly_chart(fig, use_container_width=True)

    # =============================
    # DETECCIÓN SIMPLE DE ANOMALÍAS
    # =============================
    st.subheader("🚨 Detección de anomalías")

    threshold_temp = st.slider("Umbral de temperatura", 0, 100, 35)

    anomalies = df_filtered[df_filtered["temperature"] > threshold_temp]

    st.write(f"Se detectaron {len(anomalies)} anomalías")

    fig = px.scatter(
        anomalies,
        x="timestamp",
        y="temperature",
        color="device_id",
        title="Anomalías de temperatura"
    )
    st.plotly_chart(fig, use_container_width=True)

    # =============================
    # ESTADO DE DISPOSITIVOS
    # =============================
    st.subheader("🔌 Estado de dispositivos")

    status_count = df_filtered['status'].value_counts().reset_index()
    status_count.columns = ['status', 'count']

    fig = px.pie(status_count, names='status', values='count')
    st.plotly_chart(fig, use_container_width=True)

    # =============================
    # TABLA DE DATOS
    # =============================
    st.subheader("📄 Datos")
    st.dataframe(df_filtered)

else:
    st.info("Por favor carga un archivo CSV para comenzar.")
