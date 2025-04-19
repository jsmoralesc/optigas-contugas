import streamlit as st
import pandas as pd
import sqlite3

def obtener_clientes():
    conn = sqlite3.connect("db/optigas.db")
    clientes = pd.read_sql("SELECT DISTINCT cliente_id FROM gold_anomalias", conn)
    conn.close()
    return sorted(clientes['cliente_id'].tolist())

def mostrar_kpis(cliente="Todos", fecha=None):
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT * FROM gold_anomalias", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    conn.close()

    if cliente != "Todos":
        df = df[df['cliente_id'] == cliente]
    if fecha:
        df = df[df['timestamp'] >= pd.to_datetime(fecha)]

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Volumen Total (m³)", f"{df['volumen'].sum():,.2f}")
    col2.metric("📈 Consumo Promedio Diario", f"{df.groupby(df['timestamp'].dt.date)['volumen'].sum().mean():,.2f}")
    col3.metric("⚠️ Porcentaje de Lecturas Anómalas", f"{(df['severidad'] != 'Baja').mean() * 100:.2f}%")

    col4, col5 = st.columns(2)
    col4.metric("🧪 Clientes Monitoreados", df['cliente_id'].nunique())
    col5.metric("🚨 Total Alertas (3 días)", df[df['timestamp'] >= df['timestamp'].max() - pd.Timedelta(days=3)].shape[0])
