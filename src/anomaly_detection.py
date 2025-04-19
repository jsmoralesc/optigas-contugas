import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

DB_PATH = "db/optigas.db"

def entrenar_modelos_y_guardar(db_path):
    conn = sqlite3.connect(db_path)

    # Cargar la tabla gold
    df = pd.read_sql("SELECT * FROM gold_lecturas_completas", conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Seleccionar variables para el modelo
    X = df[['presion', 'temperatura', 'volumen']]

    # Isolation Forest
    model_iso = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly_isoforest'] = model_iso.fit_predict(X)

    # One-Class SVM
    model_svm = OneClassSVM(nu=0.05, kernel="rbf", gamma='scale')
    df['anomaly_ocsvm'] = model_svm.fit_predict(X)

    # Asignar severidad básica (solo ejemplo: -1 = anomalía)
    df['severidad'] = df[['anomaly_isoforest', 'anomaly_ocsvm']].apply(
        lambda x: 'Alta' if (x == -1).all() else ('Media' if -1 in x.values else 'Baja'),
        axis=1
    )

    # Guardar resultados
    df.to_sql("gold_anomalias", conn, if_exists="replace", index=False)
    conn.close()

    print("✅ Modelos entrenados y resultados guardados en gold_anomalias")

if __name__ == "__main__":
    entrenar_modelos_y_guardar(DB_PATH)
