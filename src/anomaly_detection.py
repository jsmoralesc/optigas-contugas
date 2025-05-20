import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
import numpy as np

DB_PATH = "db/optigas.db"
Cliente ={
    "CLIENTE1":{'mf':0.8,'nt':200,'cnt':0.01},
    "CLIENTE2":{'mf':0.8,'nt':50,'cnt':0.01},
    "CLIENTE3":{'mf':0.8,'nt':100,'cnt':0.01},
    "CLIENTE4":{'mf':0.8,'nt':200,'cnt':0.01},
    "CLIENTE5":{'mf':0.8,'nt':500,'cnt':0.01},
    "CLIENTE6":{'mf':0.8,'nt':500,'cnt':0.01},
    "CLIENTE7":{'mf':0.8,'nt':100,'cnt':0.01},
    "CLIENTE8":{'mf':0.5,'nt':100,'cnt':0.1},
    "CLIENTE9":{'mf':0.8,'nt':500,'cnt':0.05},
    "CLIENTE10":{'mf':0.8,'nt':200,'cnt':0.01},
    "CLIENTE11":{'mf':0.5,'nt':500,'cnt':0.01},
    "CLIENTE12":{'mf':0.8,'nt':50,'cnt':0.01},
    "CLIENTE13":{'mf':0.8,'nt':100,'cnt':0.05},
    "CLIENTE14":{'mf':0.5,'nt':500,'cnt':0.01},
    "CLIENTE15":{'mf':0.8,'nt':100,'cnt':0.05},
    "CLIENTE16":{'mf':0.5,'nt':500,'cnt':0.1},
    "CLIENTE17":{'mf':0.8,'nt':200,'cnt':0.01},
    "CLIENTE18":{'mf':0.8,'nt':100,'cnt':0.01},
    "CLIENTE19":{'mf':0.8,'nt':50,'cnt':0.1},
    "CLIENTE20":{'mf':0.8,'nt':200,'cnt':0.01},
}


def entrenar_por_cliente(db_path):
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
        # Crear una condición para detectar cuando alguna variable es 0 y las otras > 0
        condicion_cero =(
            ((df['presion'] == 0) & (df['temperatura'] > 0) & (df['volumen'] > 0)) |  # presión es 0
            ((df['temperatura'] == 0) & (df['presion'] > 0) & (df['volumen'] > 0))   # temperatura es 0
        )  # volumen es 0
        # Combinar todas las alertas      
        df['alerta_reglas'] = df['alerta_presion'] | df['alerta_temperatura'] | condicion_cero
    # ---- 2. Detección por Modelos de ML ---- #
        features = ['Presion_scaled', 'Temperatura_scaled', 'Volumen_scaled']
        iso = IsolationForest( n_estimators=Cliente[cliente]['nt'], contamination=Cliente[cliente]['cnt'], max_features=Cliente[cliente]['mf'], random_state=42)
        iso_pred = iso.fit_predict(df[features])
        df['Anomalia_iso'] = np.where(iso_pred == -1, 1, 0)
    # ---- 3. Severidad Combinada (Reglas + ML) ---- #
        df['severidad'] = df.apply(lambda row: 
            'Alto' if row['alerta_reglas'] == 1
            else 'Potencial' if row['Anomalia_iso'] == 1  
            else 'OK', axis=1)
        # Guardar resultados
        resultados.append(df)

    df_resultado = pd.concat(resultados)
    df_resultado.drop(columns=['index'], inplace=True)
    df_resultado.reset_index(inplace=True)
    df_resultado.to_sql("gold_anomalias", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Datos procesados con reglas + ML")

if __name__ == "__main__":
    entrenar_por_cliente(DB_PATH)