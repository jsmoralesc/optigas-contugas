import streamlit as st
import sqlite3
import pandas as pd

def mostrar_comparacion(cliente_id):
    st.markdown("### 📊 Comparación con Normativa OIML R137")

    # Cargar datos
    conn = sqlite3.connect("db/optigas.db")
    df_fisica = pd.read_sql("SELECT cliente_id, timestamp, tipo_anomalia_fisica FROM gold_validacion_fisica", conn)
    df_modelo = pd.read_sql("SELECT cliente_id, timestamp, anomalia_iso, anomalia_svm FROM gold_anomalias", conn)
    conn.close()

    # Filtrar por cliente_id
    df_fisica = df_fisica[df_fisica['cliente_id'] == cliente_id]
    df_modelo = df_modelo[df_modelo['cliente_id'] == cliente_id]


    # Unir
    df = pd.merge(df_modelo, df_fisica, on=['cliente_id', 'timestamp'], how='left')

    def clasificar_evento(row):
        if row['tipo_anomalia_fisica'] == 'fuera_rango_fisico':
            if row['anomalia_iso'] == 1 or row['anomalia_svm'] == 1:
                return 'coincidencia_fisica_y_modelo'
            else:
                return 'solo_fisica'
        else:
            if row['anomalia_iso'] == 1 or row['anomalia_svm'] == 1:
                return 'solo_modelo'
            else:
                return 'normal'

    df['clasificacion_anomalia'] = df.apply(clasificar_evento, axis=1)

    # Mostrar resumen
    # Calcular distribución porcentual por tipo de coincidencia
    conteo_clasificaciones = df['clasificacion_anomalia'].value_counts(normalize=True)

    # Convertir a DataFrame y formatear porcentajes
    resumen_clasificacion = conteo_clasificaciones.rename("Proporción").reset_index()
    resumen_clasificacion.columns = ['Tipo de Evento', 'Proporción']
    resumen_clasificacion['Proporción (%)'] = (resumen_clasificacion['Proporción'] * 100).round(2)

    # 🧾 Explicación complementaria basada en la normativa OIML R137
    st.markdown("### 📘 Validación Física según Normativa OIML R137")
    st.markdown("""
    Para complementar la detección basada en modelos, se evaluó la **coherencia física de los datos** siguiendo referencias de la **normativa OIML R137**, considerando:

    | Variable    | Rango Sugerido (Estimado)                         |
    |-------------|---------------------------------------------------|
    | **Presión**     | 0.5 – 6 bar *(equivalente a 50 – 600 kPa)*         |
    | **Temperatura** | 0 °C – 60 °C *(ambiente/flujo típico de gas natural)* |
    | **Volumen**     | > 0 *(debe ser siempre positivo y realista)*        |

    Estos criterios permiten identificar valores atípicos que, aunque no sean detectados por el modelo, pueden indicar problemas de medición, fallas de sensores o condiciones operativas anómalas.
    """)
    st.info("💡 Los eventos clasificados como `solo_fisica` representan datos fuera de estos rangos aceptables.")

    # Mostrar tabla de resumen
    st.markdown("### 📊 Resumen de Clasificación de Anomalías")
    st.dataframe(resumen_clasificacion, use_container_width=True)

    # Mostrar gráfico de barras
    st.markdown("### 📈 Distribución Visual")
    st.bar_chart(resumen_clasificacion.set_index("Tipo de Evento"))

