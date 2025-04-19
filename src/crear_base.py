import sqlite3

# Crear base de datos
conn = sqlite3.connect("db/optigas.db")  # Crea el archivo si no existe
cursor = conn.cursor()

# Crear una tabla ejemplo
cursor.execute("""
CREATE TABLE IF NOT EXISTS ejemplo_cliente (
    cliente_id TEXT,
    timestamp TEXT,
    presion REAL,
    temperatura REAL,
    volumen REAL
)
""")

# Insertar un dato de prueba
cursor.execute("""
INSERT INTO ejemplo_cliente (cliente_id, timestamp, presion, temperatura, volumen)
VALUES ('C001', '2025-04-18 10:00:00', 4.3, 23.1, 120.0)
""")

conn.commit()
conn.close()
print("Base de datos y tabla creadas correctamente.")
