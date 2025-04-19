import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

def visualizar_variables(cliente="Todos", fecha=None):
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT * FROM gold_anomalias", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    conn.close()

    if cliente != "Todos":
        df = df[df['cliente_id'] == cliente]
    if fecha:
        df = df[df['timestamp'] >= pd.to_datetime(fecha)]

    st.markdown("## 📈 Evolución de Variables Operativas")

    ### Serie de tiempo
    fig, ax = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    sns.lineplot(data=df, x='timestamp', y='volumen', ax=ax[0])
    ax[0].set_title("Volumen a lo largo del tiempo")

    sns.lineplot(data=df, x='timestamp', y='presion', ax=ax[1])
    ax[1].set_title("Presión a lo largo del tiempo")

    sns.lineplot(data=df, x='timestamp', y='temperatura', ax=ax[2])
    ax[2].set_title("Temperatura a lo largo del tiempo")

    st.pyplot(fig)

    ### Boxplots por variable
    if cliente == "Todos":
        st.markdown("## 📊 Comparación por Cliente (Boxplots)")

        fig, ax = plt.subplots(1, 3, figsize=(18, 5))

        sns.boxplot(data=df, x='cliente_id', y='volumen', ax=ax[0])
        ax[0].set_title("Boxplot de Volumen")
        ax[0].tick_params(axis='x', rotation=90)

        sns.boxplot(data=df, x='cliente_id', y='presion', ax=ax[1])
        ax[1].set_title("Boxplot de Presión")
        ax[1].tick_params(axis='x', rotation=90)

        sns.boxplot(data=df, x='cliente_id', y='temperatura', ax=ax[2])
        ax[2].set_title("Boxplot de Temperatura")
        ax[2].tick_params(axis='x', rotation=90)

        st.pyplot(fig)

    ### Histogramas
    st.markdown("## 📌 Distribución de Variables")

    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    sns.histplot(df['volumen'], kde=True, ax=axs[0], color="skyblue")
    axs[0].set_title("Distribución del Volumen")

    sns.histplot(df['presion'], kde=True, ax=axs[1], color="salmon")
    axs[1].set_title("Distribución de la Presión")

    sns.histplot(df['temperatura'], kde=True, ax=axs[2], color="lightgreen")
    axs[2].set_title("Distribución de la Temperatura")

    st.pyplot(fig)
