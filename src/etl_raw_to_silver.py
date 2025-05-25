import pandas as pd
import sqlite3
import numpy as np
from statsmodels.tsa.seasonal import STL
from pathlib import Path
from sklearn.preprocessing import StandardScaler, RobustScaler
import os

# Rutas de entrada/salida
EXCEL_PATH = Path("data/raw/Datos.xlsx")
DB_PATH = "db/optigas.db"
CSV_OUTPUT = "data/gold/lecturas_completas.csv"

def tratar_Duplicados(df):
    # Lista de clientes con su estrategia recomendada
    estrategias = {
        "CLIENTE2": "mediana",
        "CLIENTE3": "promedio",
        "CLIENTE8": "mediana",
        "CLIENTE11": "promedio",
        "CLIENTE16": "mediana",
        "CLIENTE18": {
            "Presion": "promedio", 
            "Temperatura": "promedio", 
            "Volumen": "mediana"
        }
    }

    # Filtrar solo los clientes con duplicados conocidos
    clientes_duplicados = estrategias.keys()
    df_filtrado = df[df['Cliente'].isin(clientes_duplicados)]

    # Agrupar y aplicar estrategia
    grupos = df_filtrado.groupby(['Cliente', 'Fecha'])

    filas_limpias = []

    for (cliente, fecha), grupo in grupos:
        if len(grupo) == 1:
            filas_limpias.append(grupo.iloc[0])
        else:
            estrategia = estrategias[cliente]
            if isinstance(estrategia, dict):
                fila = {
                    "Fecha": fecha,
                    "Cliente": cliente,
                    "Presion": grupo["Presion"].mean() if estrategia["Presion"] == "promedio" else grupo["Presion"].median(),
                    "Temperatura": grupo["Temperatura"].mean() if estrategia["Temperatura"] == "promedio" else grupo["Temperatura"].median(),
                    "Volumen": grupo["Volumen"].mean() if estrategia["Volumen"] == "promedio" else grupo["Volumen"].median()
                }
            else:
                func = grupo.median if estrategia == "mediana" else grupo.mean
                fila = func(numeric_only=True)
                fila["Fecha"] = fecha
                fila["Cliente"] = cliente
            filas_limpias.append(pd.Series(fila))

    # Crear dataFrame limpio solo con registros duplicados tratados
    df_sin_duplicados = pd.DataFrame(filas_limpias)

    # Eliminar duplicados del original y unir con la versión limpia
    df_final = pd.concat([
        df[~df.set_index(["Cliente", "Fecha"]).index.isin(df_sin_duplicados.set_index(["Cliente", "Fecha"]).index)],
        df_sin_duplicados
    ], ignore_index=True)

    return df_final

def tratar_Inexistentes(df):
    # Diccionario para guardar los nuevos DataFrames reindexados por cliente
    clientes_reindexados = {}

    # Obtener la lista única de clientes del df_final
    clientes = df['Cliente'].unique()

    # Procesar cliente por cliente
    for cliente in clientes:
        df_cliente = df[df['Cliente'] == cliente].copy()

        # Asegurarse de que la columna 'Fecha' esté en datetime y como índice
        df_cliente = df_cliente.set_index('Fecha')

        # Reindexar con el rango de fechas completo por horas, esperado
        df_cliente = df_cliente.reindex(pd.date_range(start="2019-01-14 00:00:00", end="2023-12-31 23:00:00", freq="h"))

        # Restaurar columna de cliente (porque puede perderse al reindexar)
        df_cliente['Cliente'] = cliente

        # Guardar en diccionario
        clientes_reindexados[cliente] = df_cliente
        # Unir todos los clientes reindexados en un solo DataFrame
    df_completo = pd.concat(clientes_reindexados.values(), axis=0)
    # Resetear el índice para que 'Fecha' sea una columna nuevamente
    df_completo = df_completo.reset_index().rename(columns={"index": "Fecha"})
        # Imputar valores faltantes usando interpolación lineal por cliente
    variables = ['Volumen', 'Presion', 'Temperatura']

    for var in variables:
        df_completo[var] = df_completo.groupby('Cliente')[var].transform(lambda x: x.interpolate())
        # Copia del dataset 
        
    return df_completo

# ELIMINAR TENDENCIA
def eliminar_Tendencia(df, columna):
    df_stl = pd.DataFrame()

    for cliente in df['Cliente'].unique():
        df_cliente = df[df['Cliente'] == cliente].copy()

        if df_cliente[columna].isna().sum() > 0 or len(df_cliente) < 48:
            continue  # Evita clientes con demasiados NaN o pocos datos

        try:
            # Descomposición STL: eliminamos la tendencia (trend) y mantenemos la estacionalidad
            stl = STL(df_cliente[columna], period=24)  # Periodo diario para datos horarios
            resultado = stl.fit()

            # Eliminar la tendencia (restar la tendencia)
            df_cliente[f'{columna}SinTendencia'] = df_cliente[columna] - resultado.trend
        except Exception as e:
            print(f"Error procesando cliente {cliente}: {e}")
            continue

        df_cliente = df_cliente.reset_index()
        df_stl = pd.concat([df_stl, df_cliente], ignore_index=True)

    return df_stl

def escalar_Datos(df):
    # Log-transform para Volumen antes de escalar
    df['Volumen_log'] = np.log1p(df['Volumen'])  # log(1 + x)
    df['Volumen_scaled'] = StandardScaler().fit_transform(df[['Volumen_log']])
    # Aplicar escalamiento
    df['Presion_scaled'] = RobustScaler().fit_transform(df[['Presion']])
    df['Temperatura_scaled'] = StandardScaler().fit_transform(df[['TemperaturaSinTendencia']])
    df = df.drop(['Volumen_log'], axis=1)
    return df


def procesar_hojas_excel(excel_path, db_path, export_csv=True):
    # Leer todas las hojas del archivo Excel
    print(f"\n Procesando Documeno de excel 📄")
    df_all = pd.concat([pd.read_excel(excel_path, sheet_name=name).assign(Cliente=name) 
        for name in pd.ExcelFile(excel_path).sheet_names], ignore_index=True)
    df_all['Fecha'] = pd.to_datetime(df_all['Fecha'])

    
    df=tratar_Duplicados(df_all)
    print('✅ Eliminación de datos duplicados')
    df=tratar_Inexistentes(df)
    print('✅ Imputación de datos ⏳')
    df=eliminar_Tendencia(df,'Temperatura')
    print('✅ Remoción de tendencia en la serie de tiempo de temperatura 📉')
    df=escalar_Datos(df)
    print('✅ Escalamiento de los datos 📏')
    df=df[(df['Fecha'] >= '2022-01-01')]
    df=df.rename(columns={"Fecha": "timestamp",'Presion':'presion','Volumen':'volumen','Temperatura':'temperatura','Cliente':'cliente_id'})

    # Conexión a la base de datos SQLite
    conn = sqlite3.connect(db_path)
    # Guardar como tabla "silver" en SQLite
    df.to_sql('gold_lecturas_completas', conn, if_exists="replace", index=False)
    print(f"✅ Tabla 'gold_lecturas_completas' creada con {df.shape[0]} registros.")

    if export_csv:
        os.makedirs("data/gold", exist_ok=True)
        df.to_csv(CSV_OUTPUT, index=False)
        print(f"📁 También guardado en: {CSV_OUTPUT}")

    conn.close()
    print("\n✅ Proceso completo. Base de datos actualizada.")

if __name__ == "__main__":
    procesar_hojas_excel(EXCEL_PATH, DB_PATH)