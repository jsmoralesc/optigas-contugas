# Proyecto: Optigas - Análisis Inteligente de Detección de Anomalías en el Consumo de Gas (Contugas)

Desarrollo  analítico para el caso de Contugas sobre detección de anomalías, como parte del royecto aplicado MIAD.

## 📚 Contexto

Contugas está interesada en comprender de manera más precisa los patrones de consumo de gas de sus clientes industriales, así como las variables operacionales de su línea de distribución (presión, temperatura y volumen), con el fin de detectar posibles anomalías 

## 🔍 Objetivo
Detectar anomalías en el consumo de gas natural en clientes industriales, mediante analítica avanzada y modelos analitico, integrando resultados en un dashboard interactivo para facilitar la toma de decisiones.

## 🗂️ Estructura de datos
```bash
optigas-contugas/
├── data/
│   ├── raw/       # Datos originales sin procesar
│   ├── silver/    # Datos limpios y transformados
│   └── gold/      # Datos listos para modelamiento o visualización
│
├── db/
│   └── optigas.db # Base de datos SQLite
│
├── src/
│   ├── etl_raw_to_silver.py
│   ├── etl_silver_to_gold.py
│   └── utils.py
│
├── notebooks/
│   └── 01_exploracion.ipynb
│
├── README.md
└── requirements.txt
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
python src/etl_raw_to_silver.py
python src/etl_silver_to_gold.py
python src/anomaly_detection.py
```
Esto generará:
optigas.db en la carpeta db/
Tablas: silver_<cliente>, gold_lecturas_completas, gold_anomalias

Nota: el archivo .db no está incluido en el repositorio (.gitignore) y debe generarse localmente.


## 🤝 Autores
- ANDRES ARCILA CARMONA
- DIEGO ANDRES TIBADUISA CARRILLO
- JOHAN SEBASTIAN MORALES CARO
- IBETH KARINE TERAN ENRIQUEZ
