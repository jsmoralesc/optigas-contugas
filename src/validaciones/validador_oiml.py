import pandas as pd
import numpy as np

# usar la normativa como referencia para validar rangos y coherencia física de los datos, aplicando una versión simplificada basada en buenas prácticas metrológicas
# | Variable    | Rango sugerido (estimado)                    |
# | ----------- | -------------------------------------------- |
# | Presión     | 0.5 – 6 bar *(o 50 – 600 kPa)*               |
# | Temperatura | 0 °C – 60 °C *(ambiente/flujo típico)*       |
# | Volumen     | > 0 *(siempre positivo, sin picos absurdos)* |


def validar_rangos_fisicos(df):
    df = df.copy()
    df['presion_fuera_rango'] = ~df['presion'].between(0.5, 6)
    df['temperatura_fuera_rango'] = ~df['temperatura'].between(0, 60)
    df['volumen_fuera_rango'] = df['volumen'] < 0

    df['tipo_anomalia_fisica'] = np.select(
        [
            df['presion_fuera_rango'] | df['temperatura_fuera_rango'] | df['volumen_fuera_rango']
        ],
        ['fuera_rango_fisico'],
        default='normal'
    )
    return df

