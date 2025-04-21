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

    st.markdown(f"## 🧪 Análisis Detallado - Cliente {cliente}")
    df = cargar_datos()
    df = df[df['cliente_id'] == cliente]
    
    if fecha:
        fecha_inicio, fecha_fin = fecha
        df = df[(df['timestamp'] >= pd.to_datetime(fecha_inicio)) & 
                (df['timestamp'] <= pd.to_datetime(fecha_fin))]

    # Sección de Métricas Clave
    st.markdown("### 📊 Métricas Clave")
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Consumo Total", f"{df['volumen'].sum():,.2f} m³")
    col2.metric("📈 Promedio Diario", f"{df.groupby(df['timestamp'].dt.date)['volumen'].sum().mean():,.2f} m³")
    col3.metric("📉 Días con Consumo Cero", df[df['volumen'] == 0].shape[0])

    col4, col5 = st.columns(2)
    col4.metric("🚨 Alertas Recientes (3 días)", df[df['timestamp'] >= df['timestamp'].max() - pd.Timedelta(days=3)].shape[0])
    col5.metric("📊 % Lecturas Anómalas", f"{(df['severidad'] != 'Baja').mean() * 100:.2f}%")

    # Mapeo de colores para severidad
    color_map = {"Alta": "red", "Media": "orange", "Baja": "green"}

    # Gráficos de Dispersión Interactivos
    st.markdown("### 🔍 Relación entre Variables")
    fig_scatter = make_subplots(rows=1, cols=2, 
                              subplot_titles=("Volumen vs Temperatura", "Volumen vs Presión"),
                              horizontal_spacing=0.1)
    
    # Configuración común para los scatter plots
    scatter_config = {
        'mode': 'markers',
        'marker': {'size': 8, 'opacity': 0.7},
        'hovertemplate': '<b>Fecha:</b> %{x|%Y-%m-%d %H:%M}<br><b>Valor X:</b> %{x:.2f}<br><b>Valor Y:</b> %{y:.2f}<br><b>Severidad:</b> %{text}',
    }

    # Volumen vs Temperatura
    for severity, color in color_map.items():
        df_sub = df[df['severidad'] == severity]
        fig_scatter.add_trace(
            go.Scatter(
                x=df_sub['volumen'],
                y=df_sub['temperatura'],
                name=severity,
                text=severity,
                marker={'color': color},
                **scatter_config
            ),
            row=1, col=1
        )

    # Volumen vs Presión
    for severity, color in color_map.items():
        df_sub = df[df['severidad'] == severity]
        fig_scatter.add_trace(
            go.Scatter(
                x=df_sub['volumen'],
                y=df_sub['presion'],
                name=severity,
                text=severity,
                marker={'color': color},
                showlegend=False,
                **scatter_config
            ),
            row=1, col=2
        )

    # Añadir rangos de referencia
    fig_scatter.add_hrect(y0=12, y1=50, row=1, col=1, fillcolor="green", opacity=0.1,
                         annotation_text="Rango normal temp.", annotation_position="top left")
    fig_scatter.add_hrect(y0=7.25, y1=17.4, row=1, col=2, fillcolor="green", opacity=0.1,
                         annotation_text="Rango normal presión", annotation_position="top left")

    fig_scatter.update_layout(height=500, width=1000, legend_title_text='Severidad')
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Series Temporales Interactivas
    st.markdown("### 📈 Evolución Temporal")

    # Configuración común para series temporales
    ts_config = {
        'hovertemplate': '<b>Fecha:</b> %{x|%Y-%m-%d %H:%M}<br><b>Valor:</b> %{y:.2f}<br><b>Severidad:</b> %{text}',
        'xaxis': {
            'rangeselector': {
                'buttons': [
                    {'count': 1, 'label': '1d', 'step': 'day', 'stepmode': 'backward'},
                    {'count': 7, 'label': '1w', 'step': 'day', 'stepmode': 'backward'},
                    {'count': 1, 'label': '1m', 'step': 'month', 'stepmode': 'backward'},
                    {'step': 'all'}
                ]
            },
            'rangeslider': {'visible': True}
        }
    }

    # Función para crear gráficos temporales
    def create_time_series(y_col, title, y_range=None):
        fig = go.Figure()
        
        # Línea base
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df[y_col],
                mode='lines',
                name=y_col.capitalize(),
                line={'color': 'lightgray', 'width': 1},
                hovertemplate='<b>Fecha:</b> %{x|%Y-%m-%d %H:%M}<br><b>Valor:</b> %{y:.2f}'
            )
        )
        
        # Puntos por severidad
        for severity, color in color_map.items():
            df_sub = df[df['severidad'] == severity]
            fig.add_trace(
                go.Scatter(
                    x=df_sub['timestamp'],
                    y=df_sub[y_col],
                    mode='markers',
                    name=severity,
                    text=severity,
                    marker={'color': color, 'size': 8},
                    showlegend=(y_col == 'volumen')  # Solo mostrar leyenda en el primer gráfico
                )
            )
        
        # Rango de referencia para presión y temperatura
        if y_col == 'presion':
            fig.add_hrect(y0=7.25, y1=17.4, fillcolor="green", opacity=0.1,
                         annotation_text="Rango normal", annotation_position="top left")
        elif y_col == 'temperatura':
            fig.add_hrect(y0=12, y1=50, fillcolor="green", opacity=0.1,
                         annotation_text="Rango normal", annotation_position="top left")
        
        fig.update_layout(
            title=f"{title} - Cliente {cliente}",
            height=400,
            yaxis={'range': y_range} if y_range else None,
            **ts_config
        )
        return fig

    # Gráficos individuales
    st.plotly_chart(create_time_series('volumen', 'Volumen'), use_container_width=True)
    st.plotly_chart(create_time_series('presion', 'Presión', [0, max(df['presion'])*1.1]), use_container_width=True)
    st.plotly_chart(create_time_series('temperatura', 'Temperatura'), use_container_width=True)

    # Análisis de distribución
    st.markdown("### 📊 Distribución de Variables")
    fig_dist = make_subplots(rows=1, cols=3, 
                           subplot_titles=("Distribución de Volumen", 
                                         "Distribución de Presión", 
                                         "Distribución de Temperatura"))

    for i, col in enumerate(['volumen', 'presion', 'temperatura'], 1):
        fig_dist.add_trace(
            go.Histogram(
                x=df[col],
                name=col.capitalize(),
                marker_color=['steelblue', 'salmon', 'lightgreen'][i-1],
                opacity=0.7,
                hovertemplate='<b>Rango:</b> %{x:.2f}<br><b>Frecuencia:</b> %{y}'
            ),
            row=1, col=i
        )

    fig_dist.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_dist, use_container_width=True)