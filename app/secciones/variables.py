import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

@st.cache_data
def cargar_datos():
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT * FROM gold_anomalias", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    conn.close()
    return df

def visualizar_variables(cliente="Todos", fecha=None):
    df = cargar_datos()

    if cliente != "Todos":
        df = df[df['cliente_id'] == cliente]
    if fecha:
        fecha_inicio, fecha_fin = fecha
        df = df[(df['timestamp'] >= pd.to_datetime(fecha_inicio)) & (df['timestamp'] <= pd.to_datetime(fecha_fin))]

    if cliente == "Todos":
        st.warning("Por favor selecciona un cliente para visualizar las variables operativas.")
        return

    st.markdown("## 📈 Evolución de Variables Operativas")

    fig, ax = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    sns.lineplot(data=df, x='timestamp', y='volumen', ax=ax[0], color='steelblue')
    ax[0].set_title("Volumen a lo largo del tiempo")

    sns.lineplot(data=df, x='timestamp', y='presion', ax=ax[1], color='darkred')
    ax[1].set_title("Presión a lo largo del tiempo")

    sns.lineplot(data=df, x='timestamp', y='temperatura', ax=ax[2], color='green')
    ax[2].set_title("Temperatura a lo largo del tiempo")

    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("## 📌 Distribución de Variables")

    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    sns.histplot(df['volumen'], kde=True, ax=axs[0], color="skyblue")
    axs[0].set_title("Distribución del Volumen")

    sns.histplot(df['presion'], kde=True, ax=axs[1], color="salmon")
    axs[1].set_title("Distribución de la Presión")

    sns.histplot(df['temperatura'], kde=True, ax=axs[2], color="lightgreen")
    axs[2].set_title("Distribución de la Temperatura")

    plt.tight_layout()
    st.pyplot(fig)