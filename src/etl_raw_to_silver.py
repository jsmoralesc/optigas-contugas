import pandas as pd
import sqlite3
from pathlib import Path

# Rutas de entrada/salida
EXCEL_PATH = Path("data/raw/Datos.xlsx")
DB_PATH = "db/optigas.db"

def procesar_hojas_excel(excel_path, db_path):
    # Leer todas las hojas del archivo Excel
    xls = pd.ExcelFile(excel_path)
    hojas = xls.sheet_names

    # Conexión a la base de datos SQLite
    conn = sqlite3.connect(db_path)

    for hoja in hojas:
        print(f"\n Procesando hoja: {hoja}")

        df = pd.read_excel(xls, sheet_name=hoja)
        original_shape = df.shape[0]

        # Normalización de nombres de columnas
        df.columns = [c.strip().lower() for c in df.columns]
        df = df.rename(columns={
            'fecha': 'timestamp',
            'presion': 'presion',
            'temperatura': 'temperatura',
            'volumen': 'volumen'
        })

        # Conversión de fechas
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

        # Eliminar nulos en columnas clave
        df = df.dropna(subset=['timestamp', 'presion', 'temperatura', 'volumen'])
        after_nulos = df.shape[0]

        # Eliminar duplicados por timestamp (por cliente)
        df = df.drop_duplicates(subset=['timestamp'])
        after_duplicates = df.shape[0]

        # Agregar columna de cliente
        df['cliente_id'] = hoja

        # Guardar como tabla "silver" en SQLite
        tabla_silver = f"silver_{hoja.lower()}"
        df.to_sql(tabla_silver, conn, if_exists="replace", index=False)

        print(f"✔ {original_shape} filas originales → {after_nulos} sin nulos → {after_duplicates} sin duplicados")
        print(f"✔ Tabla guardada: {tabla_silver}")

    conn.close()
    print("\n✅ Proceso completo. Base de datos actualizada.")

if __name__ == "__main__":
    procesar_hojas_excel(EXCEL_PATH, DB_PATH)
