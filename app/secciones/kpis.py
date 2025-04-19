import streamlit as st
import pandas as pd
import sqlite3

@st.cache_data
def cargar_datos():
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT * FROM gold_anomalias", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    conn.close()
    return df

def obtener_clientes():
    df = cargar_datos()
    return sorted(df['cliente_id'].unique())

def mostrar_kpis(fecha=None):
    df = cargar_datos()

    if fecha:
        fecha_inicio, fecha_fin = fecha
        df = df[(df['timestamp'] >= pd.to_datetime(fecha_inicio)) & (df['timestamp'] <= pd.to_datetime(fecha_fin))]

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Volumen Total (m³)", f"{df['volumen'].sum():,.2f}")
    col2.metric("📈 Consumo Promedio Diario", f"{df.groupby(df['timestamp'].dt.date)['volumen'].sum().mean():,.2f}")
    col3.metric("⚠️ Porc. Lecturas Anómalas", f"{(df['severidad'] != 'Baja').mean() * 100:.2f}%")

    col4, col5 = st.columns(2)
    col4.metric("🧪 Clientes Monitoreados", df['cliente_id'].nunique())
    col5.metric("🚨 Alertas (últimos 3 días)", df[df['timestamp'] >= df['timestamp'].max() - pd.Timedelta(days=3)].shape[0])