import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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
        df = df[(df['timestamp'] >= pd.to_datetime(fecha_inicio)) & 
                (df['timestamp'] <= pd.to_datetime(fecha_fin))]

    if cliente == "Todos":
        st.warning("Por favor selecciona un cliente para visualizar las variables operativas.")
        return

    st.markdown("## 📈 Evolución de Variables Operativas")
    
    # Crear figura con subplots
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("Volumen a lo largo del tiempo", 
                                      "Presión a lo largo del tiempo", 
                                      "Temperatura a lo largo del tiempo"))
    
    # Añadir trazas
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['volumen'], mode='lines', name='Volumen', line=dict(color='steelblue')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['presion'], mode='lines', name='Presión', line=dict(color='darkred')),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['temperatura'], mode='lines', name='Temperatura', line=dict(color='green')),
        row=3, col=1
    )
    
    # Actualizar diseño
    fig.update_layout(height=800, width=1000, showlegend=False)
    fig.update_xaxes(title_text="Fecha", row=3, col=1)
    
    st.plotly_chart(fig)

    st.markdown("## 📌 Distribución de Variables")
    
    # Crear figura para distribuciones
    fig_dist = make_subplots(rows=1, cols=3,
                            subplot_titles=("Distribución del Volumen",
                                          "Distribución de la Presión",
                                          "Distribución de la Temperatura"))
    
    # Añadir histogramas
    fig_dist.add_trace(
        go.Histogram(x=df['volumen'], name='Volumen', marker_color='skyblue'),
        row=1, col=1
    )
    
    fig_dist.add_trace(
        go.Histogram(x=df['presion'], name='Presión', marker_color='salmon'),
        row=1, col=2
    )
    
    fig_dist.add_trace(
        go.Histogram(x=df['temperatura'], name='Temperatura', marker_color='lightgreen'),
        row=1, col=3
    )
    
    # Actualizar diseño
    fig_dist.update_layout(height=400, width=1200, showlegend=False)
    
    st.plotly_chart(fig_dist)