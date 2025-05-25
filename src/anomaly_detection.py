import sqlite3
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
import numpy as np

DB_PATH = "db/optigas.db"
Cliente ={
    "CLIENTE1":{'eps':0.5,'min_samp':5},
    "CLIENTE2":{'eps':0.5,'min_samp':5},
    "CLIENTE3":{'eps':0.5,'min_samp':5},
    "CLIENTE4":{'eps':0.5,'min_samp':5},
    "CLIENTE5":{'eps':0.5,'min_samp':5},
    "CLIENTE6":{'eps':0.5,'min_samp':5},
    "CLIENTE7":{'eps':0.5,'min_samp':5},
    "CLIENTE8":{'eps':0.5,'min_samp':5},
    "CLIENTE9":{'eps':0.5,'min_samp':5},
    "CLIENTE10":{'eps':0.5,'min_samp':5},
    "CLIENTE11":{'eps':0.5,'min_samp':5},
    "CLIENTE12":{'eps':0.5,'min_samp':5},
    "CLIENTE13":{'eps':0.5,'min_samp':5},
    "CLIENTE14":{'eps':0.5,'min_samp':5},
    "CLIENTE15":{'eps':0.5,'min_samp':5},
    "CLIENTE16":{'eps':0.5,'min_samp':5},
    "CLIENTE17":{'eps':0.5,'min_samp':5},
    "CLIENTE18":{'eps':0.5,'min_samp':5},
    "CLIENTE19":{'eps':0.5,'min_samp':5},
    "CLIENTE20":{'eps':0.5,'min_samp':5},
}

def entrenar_por_cliente(db_path):
    # Realizar conexión a la BD
    conn = sqlite3.connect(db_path)
    df_all = pd.read_sql("SELECT * FROM gold_lecturas_completas", conn)
    df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])

    resultados = []

    for cliente in Cliente.keys():
        df=df_all[df_all['cliente_id'] == cliente].copy()
        df.set_index('timestamp', inplace=True)

        # ---- 1. Detección por Reglas de Negocio ---- #
        df['alerta_presion'] = ~df['presion'].between(7.25, 17.4) 
        df['alerta_temperatura'] = ~df['temperatura'].between(0, 50)

        # Anomalia sospechosa
        # Crear una condición para detectar cuando alguna variable es 0 y las otras > 0
        condicion_cero =(
            ((df['presion'] == 0) & (df['temperatura'] > 0) & (df['volumen'] > 0)) |  # presión es 0
            ((df['temperatura'] == 0) & (df['presion'] > 0) & (df['volumen'] > 0))   # temperatura es 0
        )  # volumen es 0

        # Combinar todas las alertas      
        df['alerta_reglas'] = df['alerta_presion'] | df['alerta_temperatura'] | condicion_cero

    # ---- 2. Detección por Modelos de ML ---- #
        features = ['Presion_scaled', 'Temperatura_scaled', 'Volumen_scaled']
        model = DBSCAN( min_samples=Cliente[cliente]['min_samp'], eps=Cliente[cliente]['eps'], random_state=42)
        dbscan_pred = model.fit_predict(df[features])
        dbscan_labels = [1 if label == -1 else 0 for label in dbscan_labels]
        df['Anomalia_iso'] = np.where(iso_pred == -1, 1, 0)
    

    # ---- 3. Severidad Combinada (Reglas + ML) ---- #
        df['severidad'] = df.apply(lambda row: 
            'Alto' if row['alerta_reglas'] == 1
            else 'Potencial' if row['Anomalia_iso'] == 1  
            else 'OK', axis=1)
        # Guardar resultados
        resultados.append(df)

    df_resultado = pd.concat(resultados)
    df_resultado.to_csv("data/gold/results.csv")
    df_resultado.drop(columns=['index'], inplace=True)
    df_resultado.reset_index(inplace=True)
    df_resultado.to_sql("gold_anomalias", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Datos procesados con reglas + ML")

if __name__ == "__main__":
    entrenar_por_cliente(DB_PATH)