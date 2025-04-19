import streamlit as st
import pandas as pd
import sqlite3

from secciones import kpis, alertas, variables, cliente_detalle, resumen

# Configuración general de la app
st.set_page_config(page_title="OptiGas - Análisis de Anomalías", layout="wide")
st.title("🔍 OptiGas – Análisis Inteligente de Anomalías en el Consumo de Gas")

# Funciones auxiliares para obtener fechas extremas
def obtener_fecha_extremos():
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT MIN(timestamp) as min_fecha, MAX(timestamp) as max_fecha FROM gold_anomalias", conn)
    conn.close()
    return pd.to_datetime(df["min_fecha"].iloc[0]), pd.to_datetime(df["max_fecha"].iloc[0])

# Filtros globales
with st.sidebar:
    st.header("🎛️ Filtros")

    clientes = ["Todos"] + kpis.obtener_clientes()
    cliente = st.selectbox("Cliente", options=clientes)

    fecha_min_data, fecha_max_data = obtener_fecha_extremos()

    fechas = st.date_input(
        "Rango de fechas",
        value=(fecha_min_data, fecha_max_data),
        min_value=fecha_min_data,
        max_value=fecha_max_data
    )

    severidades = st.multiselect(
        "Severidad",
        options=["Alta", "Media", "Baja"],
        default=["Alta", "Media", "Baja"]
    )

# Validación del rango de fechas seleccionado
fecha_inicio, fecha_fin = fechas
fecha_inicio = pd.to_datetime(fecha_inicio)
fecha_fin = pd.to_datetime(fecha_fin)
if fecha_inicio < fecha_min_data or fecha_fin > fecha_max_data:
    st.warning(f"Se ajustó el rango a los datos disponibles: {fecha_min_data.date()} → {fecha_max_data.date()}")
    fecha_inicio = fecha_min_data
    fecha_fin = fecha_max_data


# 🧮 KPIs principales
kpis.mostrar_kpis(fecha=(fecha_inicio, fecha_fin))

# 🚨 Alertas recientes
st.markdown("## 🚨 Alertas Recientes")
alertas.mostrar_alertas(cliente=cliente, fecha=(fecha_inicio, fecha_fin), severidades=severidades)

# 📈 Visualización de variables operativas
variables.visualizar_variables(cliente=cliente, fecha=(fecha_inicio, fecha_fin))

# 🧪 Análisis detallado del cliente
cliente_detalle.visualizar_cliente(cliente=cliente, fecha=(fecha_inicio, fecha_fin))

# 🧾 Tabla resumen por cliente
resumen.mostrar_tabla_resumen(fecha=(fecha_inicio, fecha_fin))