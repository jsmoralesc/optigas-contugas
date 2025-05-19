import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

@st.cache_data
def cargar_datos():
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT * FROM gold_anomalias", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    conn.close()
    return df

def mostrar_alertas(cliente="Todos", fecha=None, severidades=None):
    df = cargar_datos()

    if cliente != "Todos":
        df = df[df['cliente_id'] == cliente]
    if fecha:
        fecha_inicio, fecha_fin = fecha
        df = df[(df['timestamp'] >= pd.to_datetime(fecha_inicio)) & (df['timestamp'] <= pd.to_datetime(fecha_fin))]
    if severidades:
        df = df[df['severidad'].isin(severidades)]

    # Filtrar alertas recientes
    df_alertas = df[df['severidad'] != "Baja"].sort_values(by="timestamp", ascending=False)
    df_ultimos3 = df_alertas[df_alertas['timestamp'] >= df_alertas['timestamp'].max() - pd.Timedelta(days=3)]

    # Layout en dos columnas
    col1, col2 = st.columns([2,3])

    with col1:
        st.subheader("🚨 Alertas recientes de anomalías (últimas 50)")

        # Ordenar por timestamp descendente y tomar las 50 más recientes
        df_alertas_ordenadas = df_alertas.sort_values(by="timestamp", ascending=False).head(50)

        st.dataframe(
            df_alertas_ordenadas[['timestamp', 'cliente_id', 'presion', 'temperatura', 'volumen', 'severidad']],
            use_container_width=True
        )



    # 1️⃣ Identificar top 5 clientes con más alertas en los últimos 3 días
    top_clientes = (
        df_ultimos3['cliente_id']
        .value_counts()
        .head(5)
        .index
        .tolist()
    )

    # 2️⃣ Filtrar datos SOLO de los últimos 3 días
    df_top_anom = df_ultimos3[df_ultimos3['cliente_id'].isin(top_clientes)]


    with col2:
        st.subheader("📊 Visualización de variables operativas y anomalías (últimos 3 días)")

        if df_ultimos3.empty:
            st.info("No hay alertas registradas en los últimos 3 días.")
            return

        variable = st.selectbox("Selecciona variable a visualizar", ["presion", "temperatura", "volumen"])


        # 🔹 Serie de tiempo (solo últimos 3 días)
        fig_time = px.line(
            df_top_anom,
            x="timestamp", y=variable, color="cliente_id",
            title=f"Serie de tiempo – {variable.title()} (últimos 3 días – Top 5 clientes)",
            labels={"timestamp": "Fecha", variable: variable.title()}
        )

        fig_time.add_scatter(
            x=df_top_anom["timestamp"],
            y=df_top_anom[variable],
            mode="markers",
            marker=dict(color="red", size=7, symbol="x"),
            name="Anomalías"
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # 🔹 Boxplot y gráfico de barras en la misma fila
    colb1, colb2 = st.columns(2)

    with colb1:
        fig_box = px.box(
            df_top_anom, x="cliente_id", y=variable, color="cliente_id",
            title=f"Distribución – {variable.title()} (últimos 3 días – Top 5)"
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with colb2:
        conteo = df_top_anom['cliente_id'].value_counts().reset_index()
        conteo.columns = ['cliente_id', 'n_anomalias']
        fig_bar = px.bar(
            conteo, x="cliente_id", y="n_anomalias", text="n_anomalias",
            title="Top 5 clientes con más alertas (últimos 3 días)"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

