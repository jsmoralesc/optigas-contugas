import streamlit as st
from secciones import kpis, alertas, variables


st.set_page_config(page_title="OPTIGAS - Análisis de Anomalías", layout="wide")

st.markdown("# 🔍 OPTIGAS - Detección de Anomalías en el Consumo de Gas")

# Filtros globales
st.sidebar.title("⚙️ Filtros")
filtro_cliente = st.sidebar.selectbox("Seleccionar cliente", options=["Todos"] + kpis.obtener_clientes())
filtro_fecha = st.sidebar.date_input("Fecha mínima", value=None)

# KPIs
kpis.mostrar_kpis(cliente=filtro_cliente, fecha=filtro_fecha)

# Tabla de alertas
st.markdown("## 🚨 Alertas recientes")
alertas.mostrar_alertas(cliente=filtro_cliente, fecha=filtro_fecha)

# visualizacion de variables operativas
st.markdown("## 📊 Visualización de Variables Operativas")
variables.visualizar_variables(cliente=filtro_cliente, fecha=filtro_fecha)

