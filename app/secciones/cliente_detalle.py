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

def visualizar_cliente(cliente="Todos", fecha=None):
    if cliente == "Todos":
        st.info("Selecciona un cliente para ver su análisis detallado.")
        return

    st.markdown("## 🧪 Comportamiento de Variables por Cliente")
    df = cargar_datos()
    df = df[df['cliente_id'] == cliente]
    if fecha:
        fecha_inicio, fecha_fin = fecha
        df = df[(df['timestamp'] >= pd.to_datetime(fecha_inicio)) & (df['timestamp'] <= pd.to_datetime(fecha_fin))]

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Consumo Total", f"{df['volumen'].sum():,.2f} m³")
    col2.metric("📈 Promedio Diario", f"{df.groupby(df['timestamp'].dt.date)['volumen'].sum().mean():,.2f} m³")
    col3.metric("📉 Días con Consumo Cero", df[df['volumen'] == 0].shape[0])

    col4, col5 = st.columns(2)
    col4.metric("🚨 Alertas (3 días)", df[df['timestamp'] >= df['timestamp'].max() - pd.Timedelta(days=3)].shape[0])
    col5.metric("📊 % Lecturas Anómalas", f"{(df['severidad'] != 'Baja').mean() * 100:.2f}%")

    st.markdown("### 🔎 Gráficos de Dispersión con Codificación por Severidad")

    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    sns.scatterplot(data=df, x='volumen', y='temperatura', hue='severidad', ax=axs[0])
    axs[0].set_title("Volumen vs Temperatura")

    sns.scatterplot(data=df, x='volumen', y='presion', hue='severidad', ax=axs[1])
    axs[1].set_title("Volumen vs Presión")

    st.pyplot(fig)


    st.markdown("### 📈 Serie Temporal del Volumen")
    colores = {"Alta": "red", "Media": "orange", "Baja": "green"}
    fig, ax = plt.subplots(figsize=(14, 5))
    for severidad, color in colores.items():
        sub = df[df['severidad'] == severidad]
        ax.scatter(sub['timestamp'], sub['volumen'], label=severidad, color=color, s=10)

    ax.plot(df['timestamp'], df['volumen'], color='lightgray', label="Volumen")
    ax.set_title(f"Volumen con codificación de severidad – Cliente {cliente}")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("### 📈 Serie Temporal de presion")
    fig, ax = plt.subplots(figsize=(14, 5))
    for severidad, color in colores.items():
        sub = df[df['severidad'] == severidad]
        ax.scatter(sub['timestamp'], sub['presion'], label=severidad, color=color, s=10)
    ax.plot(df['timestamp'], df['presion'], color='lightgray', label="Presion")
    ax.set_title(f"Presion con codificación de severidad – Cliente {cliente}")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("### 📈 Serie Temporal de temperatura")
    fig, ax = plt.subplots(figsize=(14, 5))
    for severidad, color in colores.items():
        sub = df[df['severidad'] == severidad]
        ax.scatter(sub['timestamp'], sub['temperatura'], label=severidad, color=color, s=10)
    ax.plot(df['timestamp'], df['temperatura'], color='lightgray', label="Temperatura")
    ax.set_title(f"Temperatura con codificación de severidad – Cliente {cliente}")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
