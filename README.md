# Proyecto: Optigas - Análisis Inteligente de Detección de Anomalías en el Consumo de Gas (Contugas)

Desarrollo  analítico para el caso de Contugas sobre detección de anomalías, como parte del royecto aplicado MIAD.

## 📚 Contexto

Contugas está interesada en comprender de manera más precisa los patrones de consumo de gas de sus clientes industriales, así como las variables operacionales de su línea de distribución (presión, temperatura y volumen), con el fin de detectar posibles anomalías 

## 🔍 Objetivo
Detectar anomalías en el consumo de gas natural en clientes industriales, mediante analítica avanzada y modelos analitico, integrando resultados en un dashboard interactivo para facilitar la toma de decisiones.

## 🗂️ Estructura de datos
```
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

## 🤝 Autores
- ANDRES ARCILA CARMONA
- DIEGO ANDRES TIBADUISA CARRILLO
- JOHAN SEBASTIAN MORALES CARO
- IBETH KARINE TERAN ENRIQUEZ
