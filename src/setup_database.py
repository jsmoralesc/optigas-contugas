
import sqlite3
import os

# Ruta de la base de datos
DB_PATH = os.path.join("db", "optigas.db")

# Crear conexión a la base de datos
def crear_base_datos():
    if not os.path.exists("db"):
        os.makedirs("db")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla de ejemplo para almacenar datos por cliente
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros_clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        presion REAL,
        temperatura REAL,
        volumen REAL
    );
    """)

    conn.commit()
    conn.close()
    print(f"Base de datos creada correctamente en: {DB_PATH}")

if __name__ == "__main__":
    crear_base_datos()
