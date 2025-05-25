# Proyecto: OptiGas - Análisis Inteligente de Detección de Anomalías en el Consumo de Gas (Contugas S.A.C.)

Desarrollo analítico enfocado en la detección de anomalías en el consumo de gas para el caso de Contugas, como parte del proyecto aplicado del programa de Maestría en Analítica de Datos (MIAD). El objetivo es identificar comportamientos atípicos que puedan indicar fallos operativos, pérdidas o uso inusual del servicio, mediante técnicas avanzadas de análisis de datos.

## 📚 Contexto

Contugas está interesada en comprender de manera más precisa los patrones de consumo de gas de sus clientes industriales, así como las variables operacionales de su línea de distribución (presión, temperatura y volumen), con el fin de detectar posibles anomalías 

## 🔍 Objetivo
Detectar anomalías en el consumo de gas natural en clientes industriales, mediante analítica avanzada y modelos analitico, integrando resultados en un dashboard interactivo para facilitar la toma de decisiones.

## 🗂️ Estructura de datos
```bash
optigas-contugas/
├── app/
│   ├── assets/                             # Imágenes  y adjuntos
│   └── secciones/                          # scripts para el dashboard
│   └── main/                               # script principal del dashboard
├── data/
│   ├── raw/                                # Datos originales sin procesar
│   └── gold/                               # Datos listos para modelamiento o visualización
│
├── db/
│   └── optigas.db                          # Base de datos SQLite
│
├── docs/
│   └── manual_usuario.pdf                  # Manual de usuario del tablero OptiGas
│
├── Notebooks/                              
│   ├── 01_eda.ipynb                        # Análisis exploratorio de los datos (EDA)
│   ├── 02_etl_modelos_individuales.ipynb   # Proceso de ETL y pruebas del enfoque 1 - Modelos individuales
│   ├── 03_modelos_por_grupo.ipynb          # Pruebas del enfoque 2 - Modelos por grupos
│   └── 04_evaluacion_modelos.ipynb         # Cálculo de métricas y comparación modelos enfoque 1
│
├── src/
│   ├── etl_raw_to_gold.py                  # Script que realiza el ETL y compila los datos en la tabla gold
│   └── anomaly_detection.py                # Script que aplica el modelo de ML
│
├── README.md
└── environment.yml
```

## 🛠️ Tecnologías usadas
- Python 3.x
- SQLite3
- Pandas
- Streamlit
- scikit-learn

## 🚀 Configuración del Entorno

1. Clona el repositorio:
```bash
git clone https://github.com/tuusuario/optigas-contugas.git
cd optigas-contugas
```
2. Crea el entorno Conda:
```bash
conda env create -f environment.yml
```
3. Activa el entorno:
```bash
conda activate optigas
```
4. Ejecuta la app de Streamlit:
```bash
streamlit run app/main.py
```

## 🧱 Inicialización de la Base de Datos

Este proyecto utiliza SQLite como base de datos local. Para crear la base de datos `optigas.db`, asegúrate de tener el archivo original `Datos.xlsx` en la ruta `data/raw/` y luego ejecuta:

```bash
python src/etl_raw_to_gold.py
python src/anomaly_detection.py
```
Esto generará:
optigas.db en la carpeta db/
Tablas: gold/lecturas_completas

Nota: el archivo .db no está incluido en el repositorio (.gitignore) y debe generarse localmente.


## 🤝 Autores
- JOHAN SEBASTIAN MORALES CARO
- IBETH KARINE TERAN ENRIQUEZ
- ANDRES ARCILA CARMONA
- DIEGO ANDRES TIBADUISA CARRILLO
