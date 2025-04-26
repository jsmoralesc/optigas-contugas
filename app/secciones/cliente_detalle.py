import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache_data(ttl=3600)  # Cache por 1 hora
def cargar_datos():
    conn = sqlite3.connect("db/optigas.db")
    # Solo cargar las columnas necesarias
    df = pd.read_sql("""
        SELECT timestamp, cliente_id, volumen, presion, temperatura, severidad 
        FROM gold_anomalias
    """, conn)
    conn.close()
    
    # Optimizar tipos de datos
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['volumen'] = pd.to_numeric(df['volumen'], downcast='float')
    df['presion'] = pd.to_numeric(df['presion'], downcast='float')
    df['temperatura'] = pd.to_numeric(df['temperatura'], downcast='float')
    df['severidad'] = df['severidad'].astype('category')
    
    return df

def filtrar_datos(df, cliente, fecha=None):
    df_filtrado = df[df['cliente_id'] == cliente].copy()
    
    if fecha:
        fecha_inicio, fecha_fin = fecha
        mask = (df_filtrado['timestamp'] >= pd.to_datetime(fecha_inicio)) & (df_filtrado['timestamp'] <= pd.to_datetime(fecha_fin))
        df_filtrado = df_filtrado[mask]
    
    return df_filtrado

def crear_grafico_scatter(df, x_col, y_col, color_map):
    fig = go.Figure()
    
    for severity, color in color_map.items():
        df_sub = df[df['severidad'] == severity]
        fig.add_trace(
            go.Scattergl(  # Usar Scattergl en lugar de Scatter
                x=df_sub[x_col],
                y=df_sub[y_col],
                name=severity,
                mode='markers',
                marker=dict(color=color, size=6, opacity=0.6),
                hoverinfo='skip'  # Desactivar hover para mejorar rendimiento
            )
        )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=350
    )
    return fig

def crear_time_series(df, y_col, title, color_map):
    fig = go.Figure()
    
    # Línea base simplificada
    fig.add_trace(
        go.Scattergl(
            x=df['timestamp'],
            y=df[y_col],
            mode='lines',
            line=dict(color='lightgray', width=1),
            name=y_col.capitalize()
        )
    )
    
    # Muestrear datos si hay muchos puntos (>1000)
    if len(df) > 1000:
        df_sample = df.sample(1000)
    else:
        df_sample = df.copy()
    
    for severity, color in color_map.items():
        df_sub = df_sample[df_sample['severidad'] == severity]
        fig.add_trace(
            go.Scattergl(
                x=df_sub['timestamp'],
                y=df_sub[y_col],
                mode='markers',
                marker=dict(color=color, size=6),
                name=severity,
                showlegend=False
            )
        )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def visualizar_cliente(cliente="Todos", fecha=None):
    if cliente == "Todos":
        st.info("Selecciona un cliente para ver su análisis detallado.")
        return

    # Cargar datos una vez
    df_full = cargar_datos()
    df = filtrar_datos(df_full, cliente, fecha)
    
    if df.empty:
        st.warning("No hay datos disponibles para el cliente y rango de fechas seleccionado.")
        return

    st.markdown(f"## 🧪 Análisis - {cliente}")
    
    # Usar pestañas para cargar contenido bajo demanda
    tab1, tab2, tab3 = st.tabs(["📊 Métricas", "📈 Series Temporales", "📌 Detalles"])
    
    with tab1:
        mostrar_metricas(df)
        
    with tab2:
        mostrar_series_temporales(df)
        
    with tab3:
        mostrar_detalles(df)

def mostrar_metricas(df):
    st.markdown("### 📊 Métricas Clave")
    
    # Usar columnas más eficientes
    cols = st.columns(4)
    metrics = [
        ("Consumo Total", f"{df['volumen'].sum():,.0f} m³", "📦"),
        ("Promedio Diario", f"{df.groupby(df['timestamp'].dt.date)['volumen'].sum().mean():,.0f} m³", "📈"),
        ("Días Cero", df[df['volumen'] == 0].shape[0], "📉"),
        ("% Anomalías", f"{(df['severidad'] != 'Baja').mean() * 100:.1f}%", "🚨")
    ]
    
    for (name, value, icon), col in zip(metrics, cols):
        col.metric(f"{icon} {name}", value)

def mostrar_series_temporales(df):
    st.markdown("### 📈 Evolución Temporal")
    color_map = {"Alta": "red", "Media": "orange", "Baja": "green"}
    
    # Cargar gráficos bajo demanda
    with st.spinner("Cargando visualizaciones..."):
        col1, col2 = st.columns(2)
        
        with col1:
            fig = crear_time_series(df, 'volumen', 'Volumen', color_map)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig = crear_time_series(df, 'presion', 'Presión', color_map)
            st.plotly_chart(fig, use_container_width=True)
        
        fig = crear_time_series(df, 'temperatura', 'Temperatura', color_map)
        st.plotly_chart(fig, use_container_width=True)

def mostrar_detalles(df):
    st.markdown("### 🔍 Detalles Adicionales")
    
    # Mostrar tabla de resumen (muestra pequeña)
    st.dataframe(
        df.sort_values('timestamp', ascending=False).head(100)[
            ['timestamp', 'volumen', 'presion', 'temperatura', 'severidad']
        ],
        height=300,
        use_container_width=True
    )