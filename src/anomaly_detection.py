import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

# DB_PATH = "db/optigas.db"

# def entrenar_por_cliente(db_path):
#     print(" Carga los datos de clientes y resultados guardados en gold_anomalias")
#     conn = sqlite3.connect(db_path)
#     df_all = pd.read_sql("SELECT * FROM gold_lecturas_completas", conn)
#     df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])

#     resultados = []

#     for cliente in df_all['cliente_id'].unique():
#         print(" Entrenando modelos para cliente:", cliente)
#         df = df_all[df_all['cliente_id'] == cliente].copy()
#         X = df[['presion', 'temperatura', 'volumen']]

#         if len(df) < 20:
#             print(f"⚠️ Cliente {cliente} con pocos registros ({len(df)}). Se omite.")
#             continue

#         # Entrenar modelos
#             #Ambos modelos (IsolationForest y OneClassSVM) devuelven: 1: si la observación es normal -1: si la observación es anómala
#         iso = IsolationForest(contamination=0.05, random_state=42)
#         df['anomaly_isoforest'] = iso.fit_predict(X)

#         svm = OneClassSVM(nu=0.05, kernel='rbf', gamma='scale')
#         df['anomaly_ocsvm'] = svm.fit_predict(X)

#         # Asignar severidad
#             #     'Alta'  → si ambos modelos marcaron -1  (es decir, ambos detectaron anomalía) 'Media' → si al menos uno lo detectó como -1 (pero no los dos) 'Baja'  → si ninguno lo detectó como -1
#         df['severidad'] = df[['anomaly_isoforest', 'anomaly_ocsvm']].apply(
#             lambda x: 'Alta' if (x == -1).all() else ('Media' if -1 in x.values else 'Baja'),
#             axis=1
#         )

#         resultados.append(df)
        

#     # Unir resultados de todos los clientes
#     df_resultado = pd.concat(resultados, ignore_index=True)
#     df_resultado.to_sql("gold_anomalias", conn, if_exists="replace", index=False)
#     conn.close()

#     print("✅ Modelos entrenados por cliente y resultados guardados en gold_anomalias")

# if __name__ == "__main__":
#     entrenar_por_cliente(DB_PATH)

DB_PATH = "db/optigas.db"

def entrenar_por_cliente(db_path):
    conn = sqlite3.connect(db_path)
    df_all = pd.read_sql("SELECT * FROM gold_lecturas_completas", conn)
    df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
    resultados = []

    for cliente in df_all['cliente_id'].unique():
        df = df_all[df_all['cliente_id'] == cliente].copy()
        if len(df) < 20:
            print(f"⚠️ Cliente {cliente} omitido (pocos datos: {len(df)} registros)")
            continue

        X = df[['presion', 'temperatura', 'volumen']]
        
        # ---- 1. Detección por Reglas de Negocio ---- #
        df['alerta_presion'] = ~df['presion'].between(7.25, 17.4)
        df['alerta_temperatura'] = ~df['temperatura'].between(12, 50)
        df['alerta_reglas'] = df['alerta_presion'] | df['alerta_temperatura']

        # ---- 2. Detección por Modelos de ML ---- #
        iso = IsolationForest(contamination=0.05, random_state=42)
        df['anomalia_iso'] = iso.fit_predict(X)
        
        svm = OneClassSVM(nu=0.05, kernel='rbf', gamma='scale')
        df['anomalia_svm'] = svm.fit_predict(X)
        
        # ---- 3. Severidad Combinada (Reglas + ML) ---- #
        df['severidad'] = df.apply(
            lambda x: (
                'Alta' if x['alerta_reglas'] 
                else 'Alta' if (x[['anomalia_iso', 'anomalia_svm']] == -1).all() 
                else 'Media' if -1 in x[['anomalia_iso', 'anomalia_svm']].values 
                else 'Baja'
            ), axis=1
        )
        
        resultados.append(df)

    # Guardar resultados
    df_resultado = pd.concat(resultados, ignore_index=True)
    df_resultado.to_sql("gold_anomalias", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Datos procesados con reglas + ML")

if __name__ == "__main__":
    entrenar_por_cliente(DB_PATH)