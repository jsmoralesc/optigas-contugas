import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache_data(ttl=3600)  # Cache por 1 hora

def visualizar_cliente(cliente="Todos", fecha=None):
    if cliente == "Todos":
        st.info("Selecciona un cliente para ver su análisis detallado.")
        return

    df = filtrar_datos(cargar_datos(), cliente, fecha)
    
    if df.empty:
        st.warning("No hay datos disponibles para el cliente y rango de fechas seleccionado.")
        return

    st.markdown(f"## 🔍 Análisis detallado – {cliente}")

    # Crear solo dos pestañas
    tab1, tab2 = st.tabs(["📈 Evolución Histórica", "🚨 Anomalías"])

    with tab1:
        mostrar_metricas_historicas(df)
        visualizar_variables(df_filtrado=df)

    with tab2:
        mostrar_metricas_anomalias(df)
        mostrar_series_temporales(df)
        mostrar_detalles(df)
        grafico_3d_anomalias(df)

        from secciones import comparacion_modelos
        comparacion_modelos.mostrar_comparacion(cliente_id=cliente)


def cargar_datos():
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT timestamp, cliente_id, volumen, presion, temperatura, severidad FROM gold_anomalias", conn)
    conn.close()
    
    # Optimizar tipos de datos
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['severidad'] = df['severidad'].astype('category')
    return df

def filtrar_datos(df, cliente, fecha):
    fecha_inicio, fecha_fin = fecha
    df_filtrado = df[df['cliente_id'] == cliente].copy()    
    mask = (df_filtrado['timestamp'] >= pd.to_datetime(fecha_inicio)) & (df_filtrado['timestamp'] <= pd.to_datetime(fecha_fin))
    df_filtrado = df_filtrado[mask]
    
    return df_filtrado

def crear_grafico_scatter(df, x_col, y_col, color_map):
    fig = go.Figure()
    
    for severity, color in color_map.items():
        df_sub = df[df['severidad'] == severity]
        fig.add_trace(
            go.Scattergl(
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
    fig.add_trace(
        go.Scattergl(
            x=df['timestamp'],
            y=df[y_col],
            mode='lines',
            line=dict(color='lightgray', width=1),
            name=y_col.capitalize()
        )
    )   

    df_sample = df.sample(1000) if len(df) > 1000 else df.copy()# Muestrear datos si hay muchos puntos (>1000)
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

def visualizar_variables(df_filtrado):
    st.markdown("## 📈 Evolución de Variables Operativas")

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        subplot_titles=("Volumen", "Presión", "Temperatura"))

    fig.add_trace(
        go.Scatter(x=df_filtrado['timestamp'], y=df_filtrado['volumen'], 
                   mode='lines', name='Volumen', line=dict(color='steelblue')),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=df_filtrado['timestamp'], y=df_filtrado['presion'], 
                   mode='lines', name='Presión', line=dict(color='darkred')),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(x=df_filtrado['timestamp'], y=df_filtrado['temperatura'], 
                   mode='lines', name='Temperatura', line=dict(color='green')),
        row=3, col=1
    )

    fig.update_layout(height=800, showlegend=False)
    fig.update_xaxes(title_text="Fecha", row=3, col=1)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 📌 Distribución de Variables")

    fig_dist = make_subplots(rows=1, cols=3, 
                             subplot_titles=("Volumen", "Presión", "Temperatura"))

    fig_dist.add_trace(go.Histogram(x=df_filtrado['volumen'], marker_color='skyblue'), row=1, col=1)
    fig_dist.add_trace(go.Histogram(x=df_filtrado['presion'], marker_color='salmon'), row=1, col=2)
    fig_dist.add_trace(go.Histogram(x=df_filtrado['temperatura'], marker_color='lightgreen'), row=1, col=3)

    fig_dist.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_dist, use_container_width=True)



def mostrar_metricas_historicas(df):
    st.markdown("### 📊 Métricas Generales del Cliente")

    fecha_min = df['timestamp'].min().date()
    fecha_max = df['timestamp'].max().date()

    volumen_total = df['volumen'].sum()
    volumen_prom = df['volumen'].mean()
    volumen_min = df['volumen'].min()
    volumen_max = df['volumen'].max()

    presion_prom = df['presion'].mean()
    presion_min = df['presion'].min()
    presion_max = df['presion'].max()

    temp_prom = df['temperatura'].mean()
    temp_min = df['temperatura'].min()
    temp_max = df['temperatura'].max()

    cols = st.columns(2)
    cols[0].metric("📅 Fecha Mínima", f"{fecha_min}")
    cols[1].metric("📅 Fecha Máxima", f"{fecha_max}")

    cols = st.columns(3)
    cols[0].metric("⚡ Presión Mínima", f"{presion_min:.2f} bar")
    cols[1].metric("⚡ Presión Máxima", f"{presion_max:.2f} bar")
    cols[2].metric("⚡ Presión Prom.", f"{presion_prom:.2f} bar")

    cols = st.columns(3)
    cols[0].metric("🌡️ Temp. Mínima", f"{temp_min:.1f} °C")
    cols[1].metric("🌡️ Temp. Máxima", f"{temp_max:.1f} °C")
    cols[2].metric("🌡️ Temp. Promedio", f"{temp_prom:.1f} °C")

    cols = st.columns(4)
    cols[0].metric("⛽ Volumen Mínimo", f"{volumen_min:,.0f} m³")
    cols[1].metric("⛽ Volumen Máximo", f"{volumen_max:,.0f} m³")
    cols[2].metric("⛽ Volumen Promedio", f"{volumen_prom:,.1f} m³")
    cols[3].metric("⛽ Volumen Total", f"{volumen_total:,.0f} m³")

def mostrar_metricas_anomalias(df):
    st.markdown("### 🚨 Métricas de Anomalías")

    df_anom = df[df['severidad'] != 'Baja']
    total_anomalias = df_anom.shape[0]

    if df_anom.empty:
        st.info("El cliente no presenta registros de anomalías en el periodo seleccionado.")
        return

    fecha_min_anom = df_anom['timestamp'].min().date()
    fecha_max_anom = df_anom['timestamp'].max().date()

    dias_con_anomalias = df_anom['timestamp'].dt.date.nunique()
    prom_anom_por_dia = total_anomalias / dias_con_anomalias

    cols = st.columns(1)
    cols[0].metric("📅 Rango Anomalías", f"{fecha_min_anom} → {fecha_max_anom}")
    cols = st.columns(3)
    cols[0].metric("🚨 Total Anomalías", total_anomalias)
    cols[1].metric("📆 Días con Anomalías", dias_con_anomalias)
    cols[2].metric("📊 Prom. Anomalías/Día", f"{prom_anom_por_dia:.1f}")



from plotly import graph_objects as go

def grafico_3d_anomalias(df):
    df_anom = df[df['severidad'] != 'Baja']
    
    if df_anom.empty:
        st.info("El cliente no tiene registros anómalos para graficar en 3D.")
        return

    st.markdown("### 🧭 Distribución 3D de Anomalías")

    fig = go.Figure()

    # Colores por severidad
    colores = {
        "Alta": "red",
        "Media": "orange",
        "Baja": "green"
    }

    # Una traza por severidad
    for sev in df_anom['severidad'].unique():
        df_sub = df_anom[df_anom['severidad'] == sev]
        fig.add_trace(
            go.Scatter3d(
                x=df_sub['presion'],
                y=df_sub['temperatura'],
                z=df_sub['volumen'],
                mode='markers',
                marker=dict(
                    size=5,
                    color=colores.get(sev, 'gray'),
                    opacity=0.7
                ),
                name=f"Severidad: {sev}",
                text=df_sub['timestamp'].astype(str),
                hovertemplate="<br>".join([
                    "Fecha: %{text}",
                    "Presión: %{x:.2f}",
                    "Temperatura: %{y:.2f}",
                    "Volumen: %{z:.2f}"
                ])
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis_title='Presión',
            yaxis_title='Temperatura',
            zaxis_title='Volumen'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=600,
        legend_title_text="Severidad"
    )

    st.plotly_chart(fig, use_container_width=True)
