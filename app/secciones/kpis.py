import streamlit as st
import pandas as pd
import sqlite3
import requests
from io import BytesIO
import tempfile
import os
import streamlit as st


@st.cache_data
def cargar_datos():
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT * FROM gold_anomalias", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    conn.close()
    return df

# @st.cache_data
# def cargar_datos():
#     # Descargar la base de datos
#     url = "https://github.com/anfisbena/MIAD/raw/main/GPA/optigas.db"
#     response = requests.get(url)
#     response.raise_for_status()
    
#     # Guardar temporalmente en un archivo
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
#         tmp_file.write(response.content)
#         tmp_path = tmp_file.name
    
#     # Conectar a la base de datos temporal
#     conn = sqlite3.connect(tmp_path)
#     df = pd.read_sql("SELECT * FROM gold_anomalias", conn)
#     df['timestamp'] = pd.to_datetime(df['timestamp'])
#     conn.close()
    
#     # Eliminar el archivo temporal (opcional)
#     os.unlink(tmp_path)
    
#     return df



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