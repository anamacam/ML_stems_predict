import pandas as pd
import numpy as np 
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de gráficos 
sns.set(style="whitegrid")
sns.set_palette("pastel")

# Cargar los datos
file_path = 'data/processed/merged_clean.csv'
df = pd.read_csv(file_path)

# Convertir la columna a tipo datetime
df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])

# Función para determinar la fecha de Pascua usando el algoritmo de Butcher
def easter_date(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day)

# Crear un DataFrame para almacenar las fechas festivas de 2021 a 2024
years = range(2021, 2025)
holiday_dates = []

for year in years:
    # San Valentín - 14 de febrero
    holiday_dates.append({'Date': datetime(year, 2, 14), 'Holiday': 'San Valentín'})
    
    # Día de la Madre - segundo domingo de mayo
    # Encontrar el primer día del mes
    first_day = datetime(year, 5, 1)
    # Encontrar el primer domingo (0 = lunes, 6 = domingo en weekday())
    days_until_sunday = (6 - first_day.weekday()) % 7
    first_sunday = first_day + timedelta(days=days_until_sunday)
    # El segundo domingo es 7 días después
    mothers_day = first_sunday + timedelta(days=7)
    holiday_dates.append({'Date': mothers_day, 'Holiday': 'Día de la Madre'})
    
    # Día de la Independencia - 4 de julio
    holiday_dates.append({'Date': datetime(year, 7, 4), 'Holiday': 'Día de la Independencia'})
    
    # Pascua (Easter) - fecha móvil calculada con la función
    easter = easter_date(year)
    holiday_dates.append({'Date': easter, 'Holiday': 'Pascua'})
    
    # Halloween - 31 de octubre
    holiday_dates.append({'Date': datetime(year, 10, 31), 'Holiday': 'Halloween'})
    
    # Navidad - 25 de diciembre
    holiday_dates.append({'Date': datetime(year, 12, 25), 'Holiday': 'Navidad'})

# Crear DataFrame con las fechas festivas
holidays_df = pd.DataFrame(holiday_dates)

# Mostrar las fechas festivas ordenadas
print("Fechas de festividades en Estados Unidos (2021-2024):")
print(holidays_df.sort_values(by=['Date']))

# Marcamos las fechas festivas en el dataset original
# Crear un diccionario para búsqueda rápida
holiday_dict = {row['Date'].strftime('%Y-%m-%d'): row['Holiday'] for _, row in holidays_df.iterrows()}

# Añadir columna de festividad
df['Es_Festividad'] = df['Date'].dt.strftime('%Y-%m-%d').map(holiday_dict)

# Mostrar registros que coinciden con fechas festivas
fechas_festivas = df[df['Es_Festividad'].notna()]
print("\nRegistros que coinciden con fechas festivas:")
print(fechas_festivas.head(20))

# Analizar el total de tallos por festividad
if 'Stems' in df.columns:
    # Agrupar por festividad y sumar los tallos
    tallos_por_festividad = fechas_festivas.groupby('Es_Festividad')['Stems'].sum().reset_index()
    
    # Mostrar tabla de resumen
    print("\nTotal de tallos por festividad:")
    print(tallos_por_festividad)
    
    # Guardar el resultado en un archivo CSV
    tallos_por_festividad.to_csv('resultados_festividades.csv', index=False)
    print("\nResultados guardados en 'resultados_festividades.csv'")
    
    # Visualizar
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Es_Festividad', y='Stems', data=tallos_por_festividad)
    plt.title('Total de Tallos por Festividad')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('tallos_por_festividad.png')
    print("Gráfico guardado como 'tallos_por_festividad.png'") 