import streamlit as st
import pandas as pd
import sqlite3

def mostrar_alertas(cliente="Todos", fecha=None):
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT * FROM gold_anomalias", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    conn.close()

    if cliente != "Todos":
        df = df[df['cliente_id'] == cliente]
    if fecha:
        df = df[df['timestamp'] >= pd.to_datetime(fecha)]

    # Solo anomalías medias o altas
    df_alertas = df[df['severidad'] != "Baja"]
    df_alertas = df_alertas.sort_values(by="timestamp", ascending=False)

    st.dataframe(df_alertas[['timestamp', 'cliente_id', 'presion', 'temperatura', 'volumen', 'severidad']].head(50),
                 use_container_width=True)
