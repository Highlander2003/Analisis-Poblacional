# Pandas: biblioteca para manipulación y análisis de datos en DataFrames
import pandas as pd

# NumPy: biblioteca para computación numérica con arrays multidimensionales
import numpy as np

# Plotly subplots: para crear gráficos con múltiples subgráficos
from plotly.subplots import make_subplots

# Plotly graph objects: para crear gráficos interactivos personalizados
import plotly.graph_objects as go

# Plotly express: para crear gráficos interactivos de forma rápida y sencilla
import plotly.express as px

# JSON: para trabajar con archivos y datos en formato JSON
import json

# Ruta del archivo CSV original
csv_path = "unpopulation_dataportal_20250604134916.csv"

# FUNCIÓN 1: Cargar datos poblacionales desde archivo CSV
# Lee el archivo CSV con datos de población de la ONU y lo convierte en DataFrame
df = pd.read_csv(csv_path)

# FUNCIÓN 2: Limpiar y filtrar datos iniciales
# Muestra información básica sobre los datos cargados para verificación
print("Procesando datos...")
print(f"Datos cargados: {len(df)} registros")
print(f"Columnas: {df.columns.tolist()}")

# FUNCIÓN 3: Filtrar datos por género
# Filtra solo registros que contengan datos de población por edad y sexo
# Mantiene solo: 'Male', 'Female', 'Both sexes' para análisis demográfico
df_filtered = df[df['Sex'].isin(['Male', 'Female', 'Both sexes'])].copy()

# FUNCIÓN 4: Crear y categorizar rangos de edad
# Esta función principal procesa y categoriza los datos de edad en grupos demográficos
def crearRangosEdad(df):
    # Convertir columnas de edad a valores numéricos para procesamiento
    df['edad_inicio'] = pd.to_numeric(df['AgeStart'], errors='coerce')
    df['edad_fin'] = pd.to_numeric(df['AgeEnd'], errors='coerce')
    
    # Crear etiquetas de rango basadas en Age o crear desde AgeStart/AgeEnd
    df['rango_edad'] = df['Age'].fillna(
        df['edad_inicio'].astype(str) + '-' + df['edad_fin'].astype(str)
    )
    
    # SUBCATEGORIZACIÓN: Definir condiciones para grupos demográficos
    conditions = [
        (df['edad_fin'] <= 17),
        (df['edad_inicio'] >= 18) & (df['edad_fin'] <= 44),
        (df['edad_inicio'] >= 45) & (df['edad_fin'] <= 59),
        (df['edad_inicio'] >= 60) & (df['edad_fin'] <= 74),
        (df['edad_inicio'] >= 75) & (df['edad_fin'] <= 89),
        (df['edad_inicio'] >= 90)
    ]
    # Definir etiquetas descriptivas para cada grupo demográfico
    choices = [
        "Menor de edad (0-17)",
        "Adulto joven (18-44)", 
        "Adulto medio (45-59)",
        "Adulto mayor (60-74)",
        "Anciano (75-89)",
        "Anciano longevo (90+)"
    ]
    # Aplicar categorización usando np.select para asignar cada registro a su grupo
    df['categoria_edad'] = np.select(conditions, choices, default="Otros")
    return df

# FUNCIÓN 5: Aplicar procesamiento de rangos de edad
# Ejecuta la función de categorización sobre los datos filtrados
df_processed = crearRangosEdad(df_filtered)

# FUNCIÓN 6: Limpiar datos nulos y estandarizar formato temporal
# Elimina registros con valores nulos en columnas críticas (Value, Time)
df_processed = df_processed.dropna(subset=['Value', 'Time'])
# Convierte la columna Time a formato numérico para análisis temporal
df_processed['Year'] = pd.to_numeric(df_processed['Time'], errors='coerce')
# Elimina registros donde la conversión de año falló
df_processed = df_processed.dropna(subset=['Year'])

# FUNCIÓN 7: Extraer y preparar valores únicos para filtros del dashboard
# Crea listas de valores únicos que serán usados en los filtros interactivos
anios = sorted(df_processed['Year'].unique())  # Años disponibles ordenados
paises = ['Todos'] + sorted(df_processed['Location'].dropna().unique())  # Países + opción global
sexos = sorted(df_processed['Sex'].dropna().unique())  # Géneros disponibles

# FUNCIÓN 8: Mostrar resumen estadístico de los datos procesados
# Proporciona información sobre el rango temporal y cobertura geográfica
print(f"Años disponibles: {min(anios)} - {max(anios)}")
print(f"Países disponibles: {len(paises)-1}")
print(f"Datos procesados: {len(df_processed)} registros")

# FUNCIÓN 9: Exportar datos procesados a formato JSON
# Convierte el DataFrame procesado a JSON para uso en JavaScript del dashboard
data_json = df_processed.to_json(orient="records")  # Formato: lista de objetos JSON
# Guarda el archivo JSON que será leído por el frontend web
with open("poblacion_data.json", "w") as f:
    f.write(data_json)

# FUNCIÓN 10: Generar estructura HTML completa del dashboard interactivo
# Crea un dashboard web completo con HTML, CSS y JavaScript embebido
html_final = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Análisis de Población</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        /* Configuración base para scroll suave */
        html {
            scroll-behavior: smooth;
            scroll-padding-top: 80px;
        }
        
        body {
            margin: 0;
            padding: 0;
            font-family: "Source Sans Pro", sans-serif;
            background-color: #f8fafc;
            line-height: 1.6;
            overflow-x: hidden;
        }
        
        /* Barra de progreso de scroll */
        .scroll-progress {
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(90deg, #3B82F6, #1D4ED8);
            z-index: 999999;
            transition: width 0.25s ease;
        }
        
        .stApp {
            background-color: #f8fafc;
            min-height: 100vh;
        }
        
        .stAppViewContainer {
            padding: 6rem 1rem 5rem;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
        }
        
        /* Header mejorado con navegación */
        .stAppHeader {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 4rem;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            z-index: 999990;
            border-bottom: 1px solid #e6eaf1;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .stAppHeader.scrolled {
            height: 3.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        /* Navegación interna */
        .nav-menu {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            gap: 2rem;
            padding: 0 2rem;
        }
        
        .nav-item {
            color: #4b5563;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .nav-item:hover {
            color: #3B82F6;
            background-color: #eff6ff;
            transform: translateY(-2px);
        }
        
        .nav-item.active {
            color: #1D4ED8;
            background-color: #dbeafe;
        }
        
        /* Botón de scroll hacia arriba */
        .scroll-to-top {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #3B82F6, #1D4ED8);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .scroll-to-top:hover {
            transform: translateY(-3px) scale(1.1);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
        }
        
        .scroll-to-top.visible {
            display: flex;
            animation: fadeInUp 0.3s ease;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .stMainBlockContainer {
            max-width: 100%;
            padding: 0 1rem;
        }
        
        /* Secciones con animaciones de entrada */
        .section {
            margin-bottom: 3rem;
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }
        
        .section.visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        .stVerticalBlock {
            flex-direction: column;
            gap: 2rem;
        }
        
        .stHorizontalBlock {
            display: flex;
            flex-direction: row;
            gap: 1.5rem;
            align-items: stretch;
        }
        
        @media (max-width: 768px) {
            .stHorizontalBlock {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-menu {
                gap: 1rem;
                padding: 0 1rem;
            }
            
            .nav-item {
                font-size: 0.875rem;
                padding: 0.25rem 0.5rem;
            }
        }
        
        .stColumn {
            flex: 1;
            min-width: 0;
        }
        
        /* Contenedores mejorados */
        .st-key-container-filtros,
        .st-key-container-rango {
            border-radius: 15px;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
        }
        
        .st-key-container-filtros:hover,
        .st-key-container-rango:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        .stSelectbox, .stSlider {
            margin-bottom: 1rem;
        }
        
        .stSelectbox label, .stSlider label {
            font-weight: 600;
            margin-bottom: 0.75rem;
            display: block;
            color: #374151;
        }
        
        .stSelectbox select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e5e7eb;
            border-radius: 0.5rem;
            background-color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stSelectbox select:focus {
            border-color: #3B82F6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* Contenedor del slider minimalista */
        .slider-container {
            position: relative;
            margin: 1rem 0;
            padding: 1rem;
            background: white;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease;
        }
        
        .slider-container:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .slider-label {
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.75rem;
            font-size: 0.875rem;
        }
        
        /* Estilo principal del slider minimalista */
        .stSlider input[type="range"] {
            width: 100%;
            margin: 0.5rem 0;
            height: 6px;
            border-radius: 3px;
            background: #e5e7eb;
            outline: none;
            transition: all 0.2s ease;
            -webkit-appearance: none;
            appearance: none;
            cursor: pointer;
        }
        
        /* Track del slider para WebKit */
        .stSlider input[type="range"]::-webkit-slider-track {
            height: 6px;
            border-radius: 3px;
            background: #e5e7eb;
            border: none;
        }
        
        /* Thumb del slider para WebKit - minimalista */
        .stSlider input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #3B82F6;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
            transition: all 0.2s ease;
            border: 2px solid white;
        }
        
        .stSlider input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.1);
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
        }
        
        .stSlider input[type="range"]::-webkit-slider-thumb:active {
            transform: scale(0.95);
        }
        
        /* Track del slider para Mozilla - minimalista */
        .stSlider input[type="range"]::-moz-range-track {
            height: 6px;
            border-radius: 3px;
            background: #e5e7eb;
            border: none;
        }
        
        /* Thumb del slider para Mozilla - minimalista */
        .stSlider input[type="range"]::-moz-range-thumb {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #3B82F6;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
            transition: all 0.2s ease;
            border: 2px solid white;
        }
        
        .stSlider input[type="range"]::-moz-range-thumb:hover {
            transform: scale(1.1);
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
        }
        
        /* Efectos de hover en el track - minimalistas */
        .stSlider input[type="range"]:hover {
            background: #ddd6fe;
        }
        
        .stSlider input[type="range"]:focus {
            background: #ddd6fe;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }
        
        /* Indicadores de valor minimalistas */
        .slider-values {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: #6b7280;
            font-weight: 500;
            margin-top: 0.5rem;
            padding: 0 0.25rem;
        }
        
        .slider-current-value {
            background: #3B82F6;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.75rem;
            box-shadow: 0 1px 3px rgba(59, 130, 246, 0.3);
            min-width: 50px;
            text-align: center;
            transition: all 0.2s ease;
        }
        
        .slider-current-value:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.4);
        }
        
        /* Animación del progreso del slider - minimalista */
        .slider-progress {
            position: absolute;
            top: 50%;
            left: 0;
            height: 6px;
            background: #3B82F6;
            border-radius: 3px;
            transform: translateY(-50%);
            transition: all 0.2s ease;
            z-index: 1;
        }
        
        /* Estilo para el tooltip del slider - minimalista */
        .slider-tooltip {
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            opacity: 0;
            transition: all 0.2s ease;
            pointer-events: none;
            z-index: 10;
            white-space: nowrap;
        }
        
        .slider-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 4px solid transparent;
            border-top-color: rgba(0, 0, 0, 0.8);
        }
        
        .slider-tooltip.show {
            opacity: 1;
        }
        
        .stSlider:hover .slider-tooltip {
            opacity: 1;
        }
        
        /* Slider de rango dual */
        .dual-range-container {
            position: relative;
            margin: 1rem 0;
        }
        
        .dual-range-slider {
            position: relative;
            height: 6px;
            background: #e5e7eb;
            border-radius: 3px;
            margin: 1rem 0;
        }
        
        .dual-range-track {
            position: absolute;
            height: 6px;
            background: #3B82F6;
            border-radius: 3px;
            top: 0;
        }
        
        .dual-range-input {
            position: absolute;
            width: 100%;
            height: 6px;
            top: 0;
            left: 0;
            appearance: none;
            background: transparent;
            pointer-events: none;
            outline: none;
        }
        
        .dual-range-input::-webkit-slider-thumb {
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #3B82F6;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
            border: 2px solid white;
            pointer-events: auto;
            transition: all 0.2s ease;
        }
        
        .dual-range-input::-webkit-slider-thumb:hover {
            transform: scale(1.1);
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
        }
        
        .dual-range-input::-moz-range-thumb {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #3B82F6;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
            border: 2px solid white;
            pointer-events: auto;
        }
        
        .dual-range-values {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: #6b7280;
            margin-top: 0.5rem;
        }
        
        .dual-range-current {
            background: #3B82F6;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.75rem;
            text-align: center;
        }
        
        /* Métricas mejoradas */
        .stMetric {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stMetric::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3B82F6, #1D4ED8);
        }
        
        .stMetric:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .stMetric .metric-label {
            font-size: 0.75rem;
            color: #6b7280;
            margin-bottom: 0.375rem;
            font-weight: 500;
        }
        
        .stMetric .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #111827;
            background: linear-gradient(135deg, #3B82F6, #1D4ED8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Gráficos mejorados */
        .stPlotlyChart {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stPlotlyChart::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #3B82F6, #8B5CF6, #EC4899);
        }
        
        .stPlotlyChart:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        /* Alerta mejorada */
        .stAlert {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border: 1px solid #93c5fd;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .stAlert::before {
            content: '💡';
            position: absolute;
            top: 1rem;
            left: 1rem;
            font-size: 1.5rem;
        }
        
        .stAlert p {
            margin: 0;
            padding-left: 3rem;
            color: #1e40af;
            line-height: 1.6;
        }
        
        .stAlert a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s ease;
        }
        
        .stAlert a:hover {
            color: #1d4ed8;
            text-decoration: underline;
        }
        
        /* Títulos mejorados */
        h1, h2, h3 {
            color: #111827;
            margin-bottom: 1.5rem;
            position: relative;
        }
        
        h2 {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #3B82F6, #1D4ED8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        h3 {
            font-size: 1.75rem;
            font-weight: bold;
            color: #374151;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid #e5e7eb;
            margin-bottom: 2rem;
        }
        
        h3::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #3B82F6, #1D4ED8);
        }
        
        .travel-icon::before {
            content: "🌍";
            margin-right: 0.75rem;
            font-size: 2rem;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }
        
        /* Animaciones de carga */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3B82F6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Estilos para pantallas pequeñas */
        @media (max-width: 640px) {
            .stAppViewContainer {
                padding: 5rem 0.5rem 3rem;
            }
            
            h2 {
                font-size: 2rem;
            }
            
            .stMetric .metric-value {
                font-size: 1.25rem;
            }
            
            .scroll-to-top {
                bottom: 1rem;
                right: 1rem;
                width: 45px;
                height: 45px;
            }
        }
        
        /* Estilos responsive para sliders */
        @media (max-width: 640px) {
            .slider-container {
                padding: 0.75rem;
                margin: 0.75rem 0;
            }
            
            .stSlider input[type="range"]::-webkit-slider-thumb {
                width: 16px;
                height: 16px;
            }
            
            .stSlider input[type="range"]::-moz-range-thumb {
                width: 16px;
                height: 16px;
            }
            
            .slider-current-value {
                font-size: 0.7rem;
                padding: 0.2rem 0.4rem;
                min-width: 45px;
            }
        }
    </style>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root">
        <div class="stApp">
            <div class="stAppViewContainer">
                <div class="stAppHeader">
                    <!-- Header content -->
                </div>
                
                <div class="stMainBlockContainer">
                    <div class="stVerticalBlock">
                        <!-- Título principal -->
                        <div class="stElementContainer">
                            <h2><span class="travel-icon"></span>Dashboard de Análisis de Población</h2>
                        </div>
                        
                        <!-- Alerta informativa -->
                        <div class="stAlert">
                            <p>Este dashboard permite analizar la población mundial y de diferentes países a lo largo del tiempo. 
                            Se pueden observar las tendencias de la población por rango de edad y género, así como la distribución 
                            porcentual de la población en diferentes rangos de edad. Los datos utilizados provienen de la base de 
                            datos de la ONU y están disponibles en el siguiente 
                            <a href="https://population.un.org/dataportal/home/" target="_blank" rel="noopener noreferrer">enlace</a>.</p>
                        </div>
                        
                        <!-- Fila de filtros y métrica -->
                        <!-- SECCIÓN DE FILTROS PRINCIPALES DEL DASHBOARD -->
                        <!-- Ubicada en la parte superior, permite controlar qué datos se muestran en los gráficos -->
                        <div class="stHorizontalBlock">
                            <div class="stColumn">
                                <div class="st-key-container-filtros">
                                    <div class="stHorizontalBlock">
                                        <div class="stColumn">
                                            <!-- FILTRO 1: Selector de país/región -->
                                            <!-- Permite filtrar datos por un país específico o ver datos globales -->
                                            <!-- Afecta a TODOS los gráficos del dashboard -->
                                            <div class="stSelectbox">
                                                <label>Selecciona un país</label>
                                                <select id="regionFilter">
                                                    <option value="All">Todos</option>
                                                    """ + ''.join([f'<option value="{pais}">{pais}</option>' for pais in sorted(df_processed['Location'].dropna().unique())]) + """
                                                </select>
                                            </div>
                                        </div>
                                        <div class="stColumn">
                                            <!-- FILTRO 2: Deslizador de año individual (1990-2025) -->
                                            <!-- Permite seleccionar un año específico para análisis puntual -->
                                            <!-- Afecta a: Pirámide poblacional, gráfico circular y métrica de población total -->
                                            <!-- DESLIZADOR 1: Selector de año individual (1990-2025) -->
                                            <!-- Ubicado en la sección de filtros principales, lado derecho -->
                                            <div class="stSlider">
                                                <div class="slider-container">
                                                    <div class="slider-label">Selecciona un año</div>
                                                    <div style="position: relative;">
                                                        <div class="slider-progress" id="yearProgress"></div>
                                                        <input type="range" id="yearSlider" min="1990" max="2025" value="2024" step="1">
                                                        <div class="slider-tooltip" id="yearTooltip">2024</div>
                                                    </div>
                                                    <div class="slider-values">
                                                        <span>1990</span>
                                                        <div class="slider-current-value" id="yearValue">2024</div>
                                                        <span>2025</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="stColumn" style="max-width: 300px;">
                                <div class="stMetric">
                                    <div class="metric-label">Población total 2024</div>
                                    <div class="metric-value" id="totalPopulation">145,474 personas</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Fila de gráficos principales -->
                        <div class="stHorizontalBlock">
                            <div class="stColumn">
                                <div class="stPlotlyChart">
                                    <div id="pyramidChart" style="width: 100%; height: 450px;"></div>
                                </div>
                            </div>
                            <div class="stColumn">
                                <div class="stPlotlyChart">
                                    <div id="pieChart" style="width: 100%; height: 450px;"></div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Título de tendencias -->
                        <div class="stElementContainer">
                            <h3>Tendencia de la población por rango de edad</h3>
                        </div>
                        
                        <!-- Fila de gráficos de tendencias -->
                        <div class="stHorizontalBlock">
                            <div class="stColumn">
                                <div class="stPlotlyChart">
                                    <div id="trendChart1" style="width: 100%; height: 450px;"></div>
                                </div>
                            </div>
                            <div class="stColumn">
                                <div class="stPlotlyChart">
                                    <div id="trendChart2" style="width: 100%; height: 450px;"></div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Título de análisis de variación -->
                        <div class="stElementContainer">
                            <h3>Análisis de variación de la población por rango de edad</h3>
                        </div>
                        
                        <!-- Slider de rango dual -->
                        <!-- FILTRO 3: Deslizador de rango de años para comparación temporal -->
                        <!-- Permite seleccionar dos años diferentes para comparar cambios poblacionales -->
                        <!-- Afecta a: Gráficos de variación poblacional (gráficos 5 y 6) -->
                        <!-- DESLIZADOR 2: Selector de rango de años para comparación (dual slider) -->
                        <!-- Ubicado en la sección de análisis de variación, antes de los gráficos de comparación -->
                        <div class="st-key-container-rango">
                            <div class="stSlider">
                                <div class="slider-container">
                                    <div class="slider-label">Selecciona el rango de años para comparación</div>
                                    <div class="dual-range-container">
                                        <div class="dual-range-slider">
                                            <div class="dual-range-track" id="rangeTrack"></div>
                                            <!-- Deslizador para año de inicio del rango -->
                                            <input type="range" id="rangeStart" class="dual-range-input" min="1990" max="2025" value="1990" step="1">
                                            <!-- Deslizador para año final del rango -->
                                            <input type="range" id="rangeEnd" class="dual-range-input" min="1990" max="2025" value="2025" step="1">
                                        </div>
                                        <div class="dual-range-values">
                                            <span>1990</span>
                                            <div class="dual-range-current" id="rangeDisplay">1990 - 2025</div>
                                            <span>2025</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Fila de gráficos de variación -->
                        <div class="stHorizontalBlock">
                            <div class="stColumn">
                                <div class="stPlotlyChart">
                                    <div id="variationChart1" style="width: 100%; height: 450px;"></div>
                                </div>
                            </div>
                            <div class="stColumn">
                                <div class="stPlotlyChart">
                                    <div id="variationChart2" style="width: 100%; height: 450px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let globalData = [];
        
        // Cargar datos
        fetch('poblacion_data.json')
            .then(response => response.json())
            .then(data => {
                globalData = data;
                console.log('Datos cargados:', data.length, 'registros');
                console.log('Ejemplo de datos:', data[0]);
                initializeDashboard();
            })
            .catch(error => console.error('Error loading data:', error));
        
        function initializeDashboard() {
            updateCharts();
            initializeSliders();
            
            // Event listeners
            document.getElementById('regionFilter').addEventListener('change', updateCharts);
            document.getElementById('yearSlider').addEventListener('input', function() {
                updateSliderDisplay('year', this.value);
                updateCharts();
            });
            
            // Event listeners para el slider dual
            document.getElementById('rangeStart').addEventListener('input', updateDualRange);
            document.getElementById('rangeEnd').addEventListener('input', updateDualRange);
        }
        
        function initializeSliders() {
            // Inicializar slider de año
            updateSliderDisplay('year', document.getElementById('yearSlider').value);
            updateSliderProgress('yearSlider', 'yearProgress');
            
            // Inicializar slider dual
            updateDualRange();
            
            // Event listeners para efectos visuales
            const yearSlider = document.getElementById('yearSlider');
            
            yearSlider.addEventListener('input', function() {
                updateSliderProgress('yearSlider', 'yearProgress');
                updateTooltip('yearTooltip', this.value);
                animateValueChange('yearValue');
            });
            
            // Efectos de hover para tooltips
            yearSlider.addEventListener('mouseenter', function() {
                const tooltip = document.getElementById('yearTooltip');
                tooltip.style.opacity = '1';
                tooltip.classList.add('show');
            });
            
            yearSlider.addEventListener('mouseleave', function() {
                const tooltip = document.getElementById('yearTooltip');
                tooltip.style.opacity = '0';
                tooltip.classList.remove('show');
            });
        }
        
        function updateDualRange() {
            const startSlider = document.getElementById('rangeStart');
            const endSlider = document.getElementById('rangeEnd');
            const track = document.getElementById('rangeTrack');
            const display = document.getElementById('rangeDisplay');
            
            let start = parseInt(startSlider.value);
            let end = parseInt(endSlider.value);
            
            // Asegurar que el inicio no sea mayor que el final
            if (start > end) {
                if (event.target === startSlider) {
                    end = start;
                    endSlider.value = start;
                } else {
                    start = end;
                    startSlider.value = end;
                }
            }
            
            // Actualizar el track visual
            const min = parseInt(startSlider.min);
            const max = parseInt(startSlider.max);
            const startPercent = ((start - min) / (max - min)) * 100;
            const endPercent = ((end - min) / (max - min)) * 100;
            
            track.style.left = startPercent + '%';
            track.style.width = (endPercent - startPercent) + '%';
            
            // Actualizar el display
            display.textContent = start + ' - ' + end;
            
            // Actualizar gráficos
            updateCharts();
        }
        
        function animateValueChange(elementId) {
            const element = document.getElementById(elementId);
            element.style.transform = 'scale(1.1)';
            element.style.background = 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 50%, #1E3A8A 100%)';
            
            setTimeout(() => {
                element.style.transform = 'scale(1)';
                element.style.background = 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 50%, #1E40AF 100%)';
            }, 200);
        }
        
        function updateSliderDisplay(type, value) {
            if (type === 'year') {
                document.getElementById('yearValue').textContent = value;
                document.getElementById('yearTooltip').textContent = value;
            } else if (type === 'range') {
                const displayText = value + ' - 2025';
                document.getElementById('rangeValue').textContent = displayText;
                document.getElementById('rangeTooltip').textContent = displayText;
            }
        }
        
        function updateSliderProgress(sliderId, progressId) {
            const slider = document.getElementById(sliderId);
            const progress = document.getElementById(progressId);
            
            if (slider && progress) {
                const min = parseFloat(slider.min);
                const max = parseFloat(slider.max);
                const value = parseFloat(slider.value);
                const percentage = ((value - min) / (max - min)) * 100;
                
                progress.style.width = percentage + '%';
                progress.style.transition = 'all 0.2s ease';
            }
        }
        
        function updateTooltip(tooltipId, text) {
            const tooltip = document.getElementById(tooltipId);
            if (tooltip) {
                tooltip.textContent = text;
                tooltip.style.transform = 'translateX(-50%) scale(1.05)';
                setTimeout(() => {
                    tooltip.style.transform = 'translateX(-50%) scale(1)';
                }, 100);
            }
        }
        
        function updateCharts() {
            const selectedCountry = document.getElementById('regionFilter').value;
            const selectedYear = parseInt(document.getElementById('yearSlider').value);
            
            // Filtrar datos por país y año
            let filteredData = globalData.filter(d => {
                const matchCountry = selectedCountry === 'All' || d.Location === selectedCountry;
                const matchYear = parseInt(d.Year) === selectedYear;
                return matchCountry && matchYear;
            });
            
            console.log('Datos filtrados:', filteredData.length, 'registros para', selectedCountry, selectedYear);
            
            // Actualizar los 6 gráficos
            updatePyramidChart(filteredData);
            updatePieChart(filteredData);
            updateTrendChart1();
            updateTrendChart2();
            updateVariationChart1();
            updateVariationChart2();
            updateMetrics(filteredData);
        }
        
        // GRÁFICO 1: Pirámide de población por sexo
        function updatePyramidChart(data) {
            const maleData = data.filter(d => d.Sex === 'Male');
            const femaleData = data.filter(d => d.Sex === 'Female');
            
            const traces = [];
            
            if (maleData.length > 0) {
                // Agrupar por rangos de edad para hombres
                const maleAgeGroups = {};
                maleData.forEach(d => {
                    const ageGroup = d.rango_edad || d.Age || 'Sin especificar';
                    maleAgeGroups[ageGroup] = (maleAgeGroups[ageGroup] || 0) + (d.Value || 0);
                });
                
                traces.push({
                    y: Object.keys(maleAgeGroups),
                    x: Object.values(maleAgeGroups).map(v => -Math.abs(v)),
                    type: 'bar',
                    orientation: 'h',
                    name: 'Hombres',
                    marker: { color: '#3B82F6' },
                    text: Object.values(maleAgeGroups).map(v => Math.abs(v).toLocaleString()),
                    textposition: 'inside'
                });
            }
            
            if (femaleData.length > 0) {
                // Agrupar por rangos de edad para mujeres
                const femaleAgeGroups = {};
                femaleData.forEach(d => {
                    const ageGroup = d.rango_edad || d.Age || 'Sin especificar';
                    femaleAgeGroups[ageGroup] = (femaleAgeGroups[ageGroup] || 0) + (d.Value || 0);
                });
                
                traces.push({
                    y: Object.keys(femaleAgeGroups),
                    x: Object.values(femaleAgeGroups),
                    type: 'bar',
                    orientation: 'h',
                    name: 'Mujeres',
                    marker: { color: '#EC4899' },
                    text: Object.values(femaleAgeGroups).map(v => Math.abs(v).toLocaleString()),
                    textposition: 'inside'
                });
            }
            
            const selectedCountry = document.getElementById('regionFilter').value;
            const countryName = selectedCountry === 'All' ? 'el Mundo' : selectedCountry;
            const selectedYear = document.getElementById('yearSlider').value;
            
            const layout = {
                title: '<b>Pirámide de Población para ' + countryName + ' en el año ' + selectedYear + '</b>',
                xaxis: { 
                    title: 'Población',
                    tickformat: ',d'
                },
                yaxis: { title: 'Rango de edad' },
                barmode: 'overlay',
                font: { family: 'Source Sans Pro, sans-serif' },
                height: 450
            };
            
            Plotly.newPlot('pyramidChart', traces, layout);
        }
        
        // GRÁFICO 2: Distribución por categorías de edad (Pie Chart)
        function updatePieChart(data) {
            // Filtrar solo datos de ambos sexos para evitar duplicación
            const bothSexesData = data.filter(d => d.Sex === 'Both sexes');
            
            // Agrupar por categoría de edad
            const categories = {};
            bothSexesData.forEach(d => {
                const category = d.categoria_edad || 'Sin categoría';
                categories[category] = (categories[category] || 0) + (d.Value || 0);
            });
            
            const labels = Object.keys(categories);
            const values = Object.values(categories);
            const total = values.reduce((a, b) => a + b, 0);
            
            if (total === 0) {
                // Mostrar gráfico vacío si no hay datos
                Plotly.newPlot('pieChart', [{
                    labels: ['Sin datos'],
                    values: [1],
                    type: 'pie'
                }], {
                    title: '<b>No hay datos disponibles para este filtro</b>',
                    font: { family: 'Source Sans Pro, sans-serif' }
                });
                return;
            }
            
            const trace = {
                labels: labels,
                values: values,
                type: 'pie',
                textinfo: 'label+percent',
                textposition: 'outside',
                marker: {
                    colors: ['#1077FF', '#EE805E', '#59A5DA', '#EEE852', '#7DDC65', '#FF6B6B']
                }
            };
            
            const selectedYear = document.getElementById('yearSlider').value;
            const selectedCountry = document.getElementById('regionFilter').value;
            const countryName = selectedCountry === 'All' ? 'el Mundo' : selectedCountry;
            
            const layout = {
                title: '<b>Distribución de la población por rango de edad para el ' + selectedYear + ' en ' + countryName + '</b>',
                font: { family: 'Source Sans Pro, sans-serif' },
                height: 450
            };
            
            Plotly.newPlot('pieChart', [trace], layout);
        }
        
        // GRÁFICO 3: Tendencia temporal por categorías de edad
        function updateTrendChart1() {
            const selectedCountry = document.getElementById('regionFilter').value;
            
            // Filtrar por país seleccionado
            let countryData = globalData.filter(d => {
                return (selectedCountry === 'All' || d.Location === selectedCountry) && 
                       d.Sex === 'Both sexes';
            });
            
            // Obtener años únicos y ordenados
            const years = [...new Set(countryData.map(d => parseInt(d.Year)))].sort();
            const categories = [...new Set(countryData.map(d => d.categoria_edad))].filter(c => c && c !== 'Otros');
            
            const traces = categories.map((category, idx) => {
                const data = years.map(year => {
                    const yearCategoryData = countryData.filter(d => 
                        parseInt(d.Year) === year && d.categoria_edad === category
                    );
                    return yearCategoryData.reduce((sum, d) => sum + (d.Value || 0), 0);
                });
                
                const colors = ['#1077FF', '#EE805E', '#59A5DA', '#EEE852', '#7DDC65', '#FF6B6B'];
                
                return {
                    x: years,
                    y: data,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: category,
                    line: { color: colors[idx % colors.length] },
                    fill: 'tonexty',
                    stackgroup: 'one'
                };
            });
            
            const countryName = selectedCountry === 'All' ? 'el Mundo' : selectedCountry;
            
            const layout1 = {
                title: '<b>Tendencia de la población por categoría de edad en ' + countryName + '</b>',
                xaxis: { 
                    title: 'Año',
                    tickformat: 'd'
                },
                yaxis: { 
                    title: 'Población',
                    tickformat: ',d'
                },
                font: { family: 'Source Sans Pro, sans-serif' },
                height: 450
            };
            
            Plotly.newPlot('trendChart1', traces, layout1);
        }
        
        // GRÁFICO 4: Tendencia porcentual por categorías
        function updateTrendChart2() {
            const selectedCountry = document.getElementById('regionFilter').value;
            
            // Filtrar por país seleccionado
            let countryData = globalData.filter(d => {
                return (selectedCountry === 'All' || d.Location === selectedCountry) && 
                       d.Sex === 'Both sexes';
            });
            
            const years = [...new Set(countryData.map(d => parseInt(d.Year)))].sort();
            const categories = [...new Set(countryData.map(d => d.categoria_edad))].filter(c => c && c !== 'Otros').slice(0, 3);
            
            const percentTraces = categories.map((category, idx) => {
                const data = years.map(year => {
                    const yearData = countryData.filter(d => parseInt(d.Year) === year);
                    const totalYear = yearData.reduce((sum, d) => sum + (d.Value || 0), 0);
                    
                    const categoryData = yearData.filter(d => d.categoria_edad === category);
                    const categoryTotal = categoryData.reduce((sum, d) => sum + (d.Value || 0), 0);
                    
                    return totalYear > 0 ? (categoryTotal / totalYear) * 100 : 0;
                });
                
                const colors = ['#1077FF', '#EE805E', '#59A5DA'];
                
                return {
                    x: years,
                    y: data,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: category,
                    line: { color: colors[idx % colors.length] },
                    fill: 'tonexty',
                    stackgroup: 'one'
                };
            });
            
            const countryName = selectedCountry === 'All' ? 'el Mundo' : selectedCountry;
            
            const layout2 = {
                title: '<b>Tendencia porcentual de la población en ' + countryName + '</b>',
                xaxis: { 
                    title: 'Año',
                    tickformat: 'd'
                },
                yaxis: { 
                    title: 'Porcentaje (%)',
                    tickformat: '.1f'
                },
                font: { family: 'Source Sans Pro, sans-serif' },
                height: 450
            };
            
            Plotly.newPlot('trendChart2', percentTraces, layout2);
        }
        
        // GRÁFICO 5: Análisis de variación por rangos de edad específicos
        function updateVariationChart1() {
            const selectedCountry = document.getElementById('regionFilter').value;
            const startYear = parseInt(document.getElementById('rangeStart').value);
            const endYear = parseInt(document.getElementById('rangeEnd').value);
            
            // Filtrar datos para los años de comparación
            let countryData = globalData.filter(d => {
                return (selectedCountry === 'All' || d.Location === selectedCountry) && 
                       d.Sex === 'Both sexes';
            });
            
            const dataStart = countryData.filter(d => parseInt(d.Year) === startYear);
            const dataEnd = countryData.filter(d => parseInt(d.Year) === endYear);
            
            // Obtener rangos de edad únicos
            const ageRanges = [...new Set([
                ...dataStart.map(d => d.rango_edad),
                ...dataEnd.map(d => d.rango_edad)
            ])].filter(r => r).slice(0, 5); // Limitar a 5 rangos
            
            const differences = ageRanges.map(range => {
                const totalStart = dataStart.reduce((sum, d) => sum + (d.Value || 0), 0);
                const totalEnd = dataEnd.reduce((sum, d) => sum + (d.Value || 0), 0);
                
                const rangeStart = dataStart.filter(d => d.rango_edad === range).reduce((sum, d) => sum + (d.Value || 0), 0);
                const rangeEnd = dataEnd.filter(d => d.rango_edad === range).reduce((sum, d) => sum + (d.Value || 0), 0);
                
                const percentStart = totalStart > 0 ? (rangeStart / totalStart) * 100 : 0;
                const percentEnd = totalEnd > 0 ? (rangeEnd / totalEnd) * 100 : 0;
                
                return percentEnd - percentStart;
            });
            
            const trace1 = {
                x: differences,
                y: ageRanges,
                type: 'bar',
                orientation: 'h',
                marker: {
                    color: differences.map(d => d >= 0 ? '#7DDC65' : '#ED5855')
                },
                text: differences.map(d => d.toFixed(2) + '%'),
                textposition: 'outside'
            };
            
            const countryName = selectedCountry === 'All' ? 'el Mundo' : selectedCountry;
            
            const layout1 = {
                title: '<b>Variación poblacional por rango de edad (' + startYear + ' vs ' + endYear + ') - ' + countryName + '</b>',
                xaxis: { 
                    title: 'Diferencia porcentual (%)',
                    tickformat: '.1f'
                },
                yaxis: { title: 'Rango de edad' },
                font: { family: 'Source Sans Pro, sans-serif' },
                height: 450
            };
            
            Plotly.newPlot('variationChart1', [trace1], layout1);
        }
        
        // GRÁFICO 6: Análisis de variación por categorías amplias
        function updateVariationChart2() {
            const selectedCountry = document.getElementById('regionFilter').value;
            const startYear = parseInt(document.getElementById('rangeStart').value);
            const endYear = parseInt(document.getElementById('rangeEnd').value);
            
            // Filtrar datos para los años de comparación
            let countryData = globalData.filter(d => {
                return (selectedCountry === 'All' || d.Location === selectedCountry) && 
                       d.Sex === 'Both sexes';
            });
            
            const dataStart = countryData.filter(d => parseInt(d.Year) === startYear);
            const dataEnd = countryData.filter(d => parseInt(d.Year) === endYear);
            
            const categories = ['Menor de edad (0-17)', 'Adulto joven (18-44)', 'Adulto medio (45-59)'];
            
            const catDifferences = categories.map(category => {
                const totalStart = dataStart.reduce((sum, d) => sum + (d.Value || 0), 0);
                const totalEnd = dataEnd.reduce((sum, d) => sum + (d.Value || 0), 0);
                
                const catStart = dataStart.filter(d => d.categoria_edad === category).reduce((sum, d) => sum + (d.Value || 0), 0);
                const catEnd = dataEnd.filter(d => d.categoria_edad === category).reduce((sum, d) => sum + (d.Value || 0), 0);
                
                const percentStart = totalStart > 0 ? (catStart / totalStart) * 100 : 0;
                const percentEnd = totalEnd > 0 ? (catEnd / totalEnd) * 100 : 0;
                
                return percentEnd - percentStart;
            });
            
            const trace2 = {
                x: catDifferences,
                y: categories,
                type: 'bar',
                orientation: 'h',
                marker: {
                    color: catDifferences.map(d => d >= 0 ? '#7DDC65' : '#ED5855')
                },
                text: catDifferences.map(d => d.toFixed(2) + '%'),
                textposition: 'outside'
            };
            
            const countryName = selectedCountry === 'All' ? 'el Mundo' : selectedCountry;
            
            const layout2 = {
                title: '<b>Variación poblacional por categoría (' + startYear + ' vs ' + endYear + ') - ' + countryName + '</b>',
                xaxis: { 
                    title: 'Diferencia porcentual (%)',
                    tickformat: '.1f'
                },
                yaxis: { title: 'Categoría de edad' },
                font: { family: 'Source Sans Pro, sans-serif' },
                height: 450
            };
            
            Plotly.newPlot('variationChart2', [trace2], layout2);
        }
        
        // Actualizar métricas
        function updateMetrics(data) {
            const total = data.reduce((sum, d) => sum + (d.Value || 0), 0);
            const selectedYear = document.getElementById('yearSlider').value;
            
            document.getElementById('totalPopulation').textContent = 
                new Intl.NumberFormat('es-ES').format(Math.round(total)) + ' personas';
            
            // Actualizar la etiqueta de la métrica
            const metricLabel = document.querySelector('.metric-label');
            if (metricLabel) {
                metricLabel.textContent = 'Población total ' + selectedYear;
            }
        }
    </script>
</body>
</html>
"""

# Guardar el contenido HTML completo del dashboard en un archivo físico
# Se especifica encoding="utf-8" para soportar caracteres especiales en español
with open("dashboard_poblacion.html", "w", encoding="utf-8") as f:
    f.write(html_final)  # Escribir toda la estructura HTML con CSS y JavaScript embebido

# Mostrar mensaje de confirmación al usuario indicando que el archivo fue creado exitosamente
print("✅ Dashboard generado: dashboard_poblacion.html")
