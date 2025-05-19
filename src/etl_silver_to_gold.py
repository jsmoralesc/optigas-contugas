import sqlite3
import pandas as pd
import os
from src.validaciones.validador_oiml import validar_rangos_fisicos

DB_PATH = "db/optigas.db"
CSV_OUTPUT = "data/gold/lecturas_completas.csv"

def construir_tabla_gold(db_path, export_csv=True):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obtener nombres de tablas "silver_"
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [t[0] for t in cursor.fetchall() if t[0].startswith('silver_')]

    if not tablas:
        print("⚠️ No se encontraron tablas 'silver_*' en la base de datos.")
        return

    print(f"🔗 Unificando {len(tablas)} tablas en una sola tabla 'gold_lecturas_completas'...")

    df_gold = pd.DataFrame()

    for tabla in tablas:
        df = pd.read_sql(f"SELECT * FROM {tabla}", conn)
        df_gold = pd.concat([df_gold, df], ignore_index=True)

    # Conversión de tipos y ordenamiento
    df_gold['timestamp'] = pd.to_datetime(df_gold['timestamp'])
    df_gold = df_gold.sort_values(by=['cliente_id', 'timestamp'])

    # Guardar en base de datos como tabla gold
    df_gold.to_sql("gold_lecturas_completas", conn, if_exists="replace", index=False)
    print(f"✅ Tabla 'gold_lecturas_completas' creada con {df_gold.shape[0]} registros.")

    # Guardar también como archivo CSV
    if export_csv:
        os.makedirs("data/gold", exist_ok=True)
        df_gold.to_csv(CSV_OUTPUT, index=False)
        print(f"📁 También guardado en: {CSV_OUTPUT}")

    # Cargar datos recién generados
    df_gold = pd.read_sql("SELECT * FROM gold_lecturas_completas", conn)

    # Aplicar validación de rangos físicos
    df_validado = validar_rangos_fisicos(df_gold)

    # Guardar como nueva tabla
    df_validado.to_sql("gold_validacion_fisica", conn, if_exists="replace", index=False)
    print("✅ Validación física OIML aplicada y almacenada en 'gold_validacion_fisica'")

    conn.close()

if __name__ == "__main__":
    construir_tabla_gold(DB_PATH)
