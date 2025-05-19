import streamlit as st
import pandas as pd
import sqlite3

@st.cache_data


def cargar_datos():
    conn = sqlite3.connect("db/optigas.db")
    df = pd.read_sql("SELECT * FROM gold_anomalias", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['severidad'] = df['severidad'].astype('category')
    conn.close()
    return df


def mostrar_tabla_resumen(fecha=None, cliente="Todos"):
    st.markdown("## 🧾 Resumen Descriptivo por Cliente")

    df = cargar_datos()

    if cliente != "Todos":
        df = df[df['cliente_id'] == cliente]

    if fecha:
        fecha_inicio, fecha_fin = fecha
        df = df[(df['timestamp'] >= pd.to_datetime(fecha_inicio)) & (df['timestamp'] <= pd.to_datetime(fecha_fin))]

    fecha_max = df['timestamp'].max()
    fecha_corte = fecha_max - pd.DateOffset(days=30)

    resumen = df.groupby("cliente_id").agg(
        consumo_promedio=('volumen', 'mean'),
        consumo_minimo=('volumen', 'min'),
        consumo_maximo=('volumen', 'max'),
        desviacion=('volumen', 'std'),
        CUM=('volumen', lambda x: x[df.loc[x.index, 'timestamp'] >= fecha_corte].sum()),
        num_altas=('severidad', lambda x: (x == 'Alta').sum()),
        num_medias=('severidad', lambda x: (x == 'Media').sum()),
        num_bajas=('severidad', lambda x: (x == 'Baja').sum()),
        total_anomalias=('severidad', lambda x: (x != 'Baja').sum()),
        porcentaje_anomalias=('severidad', lambda x: (x != 'Baja').mean() * 100)
    ).reset_index()

    resumen['rel_CUM'] = resumen['CUM'] / resumen['consumo_promedio']

    def colorear(val, critico_bajo=0.5, critico_alto=2):
        if isinstance(val, (int, float)):
            if val < critico_bajo:
                return 'background-color: #c9b371'
            elif val > critico_alto:
                return 'background-color: #d13636'
        return ''

    # Mostrar tabla resumen
    st.dataframe(
        resumen.style.applymap(colorear, subset=['rel_CUM', 'desviacion', 'porcentaje_anomalias']),
        use_container_width=True
    )

    st.download_button(
        label="📥 Exportar resumen a CSV",
        data=resumen.to_csv(index=False).encode('utf-8'),
        file_name="resumen_clientes.csv",
        mime="text/csv"
    )

    # Tabla descriptiva de métricas debajo
    st.markdown("### 📖 Descripción de métricas")
    descripcion_metricas = pd.DataFrame({
        "Métrica": [
            "consumo_promedio", "consumo_minimo", "consumo_maximo", "desviacion",
            "CUM", "rel_CUM",
            "num_altas", "num_medias", "num_bajas", "total_anomalias", "porcentaje_anomalias"
        ],
        "Descripción": [
            "Promedio horario del volumen de gas.",
            "Mínimo volumen de gas registrado.",
            "Máximo volumen de gas registrado.",
            "Desviación estándar del consumo.",
            "Consumo total en los últimos 30 días.",
            "Relación entre CUM y el promedio histórico.",
            "Número de anomalías de severidad Alta.",
            "Número de anomalías de severidad Media.",
            "Número de lecturas normales.",
            "Total de alertas (Alta o Media).",
            "Porcentaje de registros con anomalías (Alta o Media)."
        ]
    })

    st.dataframe(descripcion_metricas, use_container_width=True)
