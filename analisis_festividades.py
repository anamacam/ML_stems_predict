import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de gráficos
sns.set(style="whitegrid")
sns.set_palette("pastel")

# Verificar la ruta del archivo
print("Directorio actual:", os.getcwd())

# Cargar los datos con la ruta correcta
try:
    file_path = 'data/processed/merged_clean.csv'
    df = pd.read_csv(file_path)
    print(f"Archivo cargado correctamente desde {file_path}")
except FileNotFoundError:
    try:
        file_path = '../data/processed/merged_clean.csv'
        df = pd.read_csv(file_path)
        print(f"Archivo cargado correctamente desde {file_path}")
    except FileNotFoundError:
        print("No se pudo encontrar el archivo. Buscando archivos CSV en el directorio...")
        # Buscar archivos csv en el directorio actual y subdirectorios
        csv_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.csv'):
                    csv_files.append(os.path.join(root, file))
        
        if csv_files:
            print("Archivos CSV encontrados:")
            for i, file in enumerate(csv_files):
                print(f"{i+1}. {file}")
            
            # Usar el primer archivo CSV encontrado
            file_path = csv_files[0]
            df = pd.read_csv(file_path)
            print(f"Usando el archivo: {file_path}")
        else:
            print("No se encontraron archivos CSV.")
            exit(1)

# Mostrar información básica del dataset
print("\nColumnas en el dataset:")
print(df.columns.tolist())

print("\nPrimeras filas del dataset:")
print(df.head())

print("\nInformación del dataset:")
df.info()

# Verificar si existen las columnas necesarias
required_cols = ['Year', 'Month', 'Day']
if not all(col in df.columns for col in required_cols):
    print("\nError: El dataset no contiene las columnas necesarias (Year, Month, Day).")
    print("Columnas disponibles:", df.columns.tolist())
    exit(1)

# Convertir a tipo datetime
df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
print("\nConversión a fecha completada.")

# Función para calcular Pascua usando el algoritmo de Butcher
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

# Determinar el rango de años a partir del dataset
min_year = df['Year'].min()
max_year = df['Year'].max()
years = range(min_year, max_year + 1)
print(f"\nAnalizando festividades para el rango de años: {min_year}-{max_year}")

# Crear un DataFrame para almacenar las fechas festivas
holiday_dates = []

for year in years:
    # San Valentín - 14 de febrero
    holiday_dates.append({'Date': datetime(year, 2, 14), 'Holiday': 'San Valentín'})
    
    # Día de la Madre - segundo domingo de mayo
    first_day = datetime(year, 5, 1)
    days_until_sunday = (6 - first_day.weekday()) % 7
    first_sunday = first_day + timedelta(days=days_until_sunday)
    mothers_day = first_sunday + timedelta(days=7)
    holiday_dates.append({'Date': mothers_day, 'Holiday': 'Día de la Madre'})
    
    # Día de la Independencia - 4 de julio
    holiday_dates.append({'Date': datetime(year, 7, 4), 'Holiday': 'Día de la Independencia'})
    
    # Pascua - fecha móvil calculada con la función
    easter = easter_date(year)
    holiday_dates.append({'Date': easter, 'Holiday': 'Pascua'})
    
    # Halloween - 31 de octubre
    holiday_dates.append({'Date': datetime(year, 10, 31), 'Holiday': 'Halloween'})
    
    # Navidad - 25 de diciembre
    holiday_dates.append({'Date': datetime(year, 12, 25), 'Holiday': 'Navidad'})

# Crear DataFrame con las fechas festivas
holidays_df = pd.DataFrame(holiday_dates)

# Mostrar las fechas festivas ordenadas
print("\nFechas de festividades para el análisis:")
print(holidays_df.sort_values(by=['Date']))

# Convertir fechas a formato string para comparar
df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')
holidays_df['Date_str'] = holidays_df['Date'].dt.strftime('%Y-%m-%d')

# Comprobar cuántas fechas del dataset coinciden con festividades
fecha_count = df['Date_str'].nunique()
fechas_festivas_count = len(set(df['Date_str']).intersection(set(holidays_df['Date_str'])))
print(f"\nEl dataset contiene {fecha_count} fechas únicas.")
print(f"De esas, {fechas_festivas_count} coinciden con festividades.")

# Crear un diccionario para búsqueda rápida
holiday_dict = {row['Date_str']: row['Holiday'] for _, row in holidays_df.iterrows()}

# Añadir columna de festividad
df['Es_Festividad'] = df['Date_str'].map(holiday_dict)

# Mostrar registros que coinciden con fechas festivas
fechas_festivas = df[df['Es_Festividad'].notna()]
print(f"\nHay {len(fechas_festivas)} registros que coinciden con fechas festivas.")

if len(fechas_festivas) == 0:
    print("\nNo se encontraron coincidencias con fechas festivas en el dataset.")
    # Verificar si hay datos cercanos a las festividades
    buffer_days = 3  # Días antes y después de cada festividad
    print(f"\nBuscando registros en un rango de ±{buffer_days} días alrededor de cada festividad...")
    
    all_holiday_dates = []
    for _, row in holidays_df.iterrows():
        holiday_date = row['Date']
        for i in range(-buffer_days, buffer_days + 1):
            near_date = holiday_date + timedelta(days=i)
            all_holiday_dates.append((near_date.strftime('%Y-%m-%d'), row['Holiday'], i))
    
    near_holiday_dict = {date: (holiday, offset) for date, holiday, offset in all_holiday_dates}
    df['Cerca_Festividad'] = df['Date_str'].map(lambda x: near_holiday_dict.get(x))
    df['Es_Festividad_Cercana'] = df['Cerca_Festividad'].apply(lambda x: x[0] if x is not None else None)
    df['Días_Offset'] = df['Cerca_Festividad'].apply(lambda x: x[1] if x is not None else None)
    
    fechas_festivas_cercanas = df[df['Es_Festividad_Cercana'].notna()]
    print(f"Se encontraron {len(fechas_festivas_cercanas)} registros cercanos a festividades.")
    
    if len(fechas_festivas_cercanas) > 0:
        fechas_festivas = fechas_festivas_cercanas
        groupby_col = 'Es_Festividad_Cercana'
    else:
        print("No se encontraron fechas cercanas a festividades tampoco.")
        exit(1)
else:
    groupby_col = 'Es_Festividad'

# Analizar el total de tallos por festividad
if 'Stems' in df.columns:
    # Agrupar por festividad y sumar los tallos
    tallos_por_festividad = fechas_festivas.groupby(groupby_col)['Stems'].sum().reset_index()
    
    # Ordenar por cantidad de tallos de mayor a menor
    tallos_por_festividad = tallos_por_festividad.sort_values(by='Stems', ascending=False)
    
    print("\nTotal de tallos por festividad (ordenado de mayor a menor):")
    print(tallos_por_festividad)
    
    # También mostrar el promedio diario para comparar
    # Añadir conteo de días por festividad
    dias_por_festividad = fechas_festivas.groupby(groupby_col)['Date_str'].nunique().reset_index()
    dias_por_festividad.columns = [groupby_col, 'Días_Únicos']
    
    tallos_promedio = tallos_por_festividad.merge(dias_por_festividad, on=groupby_col)
    tallos_promedio['Promedio_Por_Día'] = tallos_promedio['Stems'] / tallos_promedio['Días_Únicos']
    tallos_promedio = tallos_promedio.sort_values(by='Promedio_Por_Día', ascending=False)
    
    print("\nPromedio de tallos por día para cada festividad:")
    print(tallos_promedio)
    
    # Visualizar
    plt.figure(figsize=(12, 6))
    sns.barplot(x=groupby_col, y='Stems', data=tallos_por_festividad)
    plt.title('Total de Tallos por Festividad')
    plt.ylabel('Número de Tallos')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('total_tallos_por_festividad.png')
    print("\nGráfico guardado como 'total_tallos_por_festividad.png'")
    
    # Visualizar el promedio diario
    plt.figure(figsize=(12, 6))
    sns.barplot(x=groupby_col, y='Promedio_Por_Día', data=tallos_promedio)
    plt.title('Promedio Diario de Tallos por Festividad')
    plt.ylabel('Promedio de Tallos por Día')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('promedio_tallos_por_festividad.png')
    print("Gráfico guardado como 'promedio_tallos_por_festividad.png'")
    
    # Guardar resultados en CSV
    tallos_promedio.to_csv('resultados_festividades.csv', index=False)
    print("Resultados guardados en 'resultados_festividades.csv'")
    
    # Análisis adicional - Distribucion de tallos por tipo de flor para cada festividad
    if 'Flower' in df.columns:
        print("\nTop 5 flores más populares por festividad:")
        for holiday in tallos_promedio[groupby_col].unique():
            holiday_data = fechas_festivas[fechas_festivas[groupby_col] == holiday]
            top_flowers = holiday_data.groupby('Flower')['Stems'].sum().reset_index()
            top_flowers = top_flowers.sort_values(by='Stems', ascending=False).head(5)
            print(f"\n{holiday}:")
            print(top_flowers)
else:
    print("\nNo se encontró la columna 'Stems' en el dataset.")
    exit(1) 