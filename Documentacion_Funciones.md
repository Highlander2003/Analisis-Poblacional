# Documentación de Funciones - Análisis Poblacional

## Índice
1. [Funciones Python principales](#funciones-python-principales)
2. [Funciones JavaScript del Dashboard](#funciones-javascript-del-dashboard)
3. [Filtros y Deslizadores](#filtros-y-deslizadores)
4. [Gráficos](#gráficos)

---

## Funciones Python principales

### FUNCIÓN 1: Cargar datos poblacionales (Líneas 18-19)
```python
df = pd.read_csv(csv_path)
```
**Ubicación**: Línea 18-19  
**Propósito**: Lee el archivo CSV con datos de población de la ONU y lo convierte en un DataFrame de pandas para su manipulación.

### FUNCIÓN 2: Limpiar y filtrar datos iniciales (Líneas 21-25)
```python
print("Procesando datos...")
print(f"Datos cargados: {len(df)} registros")
print(f"Columnas: {df.columns.tolist()}")
```
**Ubicación**: Líneas 21-25  
**Propósito**: Muestra información básica sobre los datos cargados para verificación y depuración.

### FUNCIÓN 3: Filtrar datos por género (Líneas 27-30)
```python
df_filtered = df[df['Sex'].isin(['Male', 'Female', 'Both sexes'])].copy()
```
**Ubicación**: Líneas 29-30  
**Propósito**: Filtra solo registros que contengan datos de población por edad y sexo, manteniendo únicamente: 'Male', 'Female', 'Both sexes' para análisis demográfico.

### FUNCIÓN 4: Crear y categorizar rangos de edad (Líneas 32-64)
```python
def crearRangosEdad(df):
    # Convertir columnas de edad a valores numéricos
    df['edad_inicio'] = pd.to_numeric(df['AgeStart'], errors='coerce')
    df['edad_fin'] = pd.to_numeric(df['AgeEnd'], errors='coerce')
    
    # Crear etiquetas de rango
    df['rango_edad'] = df['Age'].fillna(
        df['edad_inicio'].astype(str) + '-' + df['edad_fin'].astype(str)
    )
    
    # Definir condiciones para grupos demográficos
    conditions = [
        (df['edad_fin'] <= 17),
        (df['edad_inicio'] >= 18) & (df['edad_fin'] <= 44),
        (df['edad_inicio'] >= 45) & (df['edad_fin'] <= 59),
        (df['edad_inicio'] >= 60) & (df['edad_fin'] <= 74),
        (df['edad_inicio'] >= 75) & (df['edad_fin'] <= 89),
        (df['edad_inicio'] >= 90)
    ]
    
    # Definir etiquetas descriptivas
    choices = [
        "Menor de edad (0-17)",
        "Adulto joven (18-44)", 
        "Adulto medio (45-59)",
        "Adulto mayor (60-74)",
        "Anciano (75-89)",
        "Anciano longevo (90+)"
    ]
    
    # Aplicar categorización
    df['categoria_edad'] = np.select(conditions, choices, default="Otros")
    return df
```
**Ubicación**: Líneas 32-64  
**Propósito**: Función principal que procesa y categoriza los datos de edad en grupos demográficos estándar.

### FUNCIÓN 5: Aplicar procesamiento de rangos de edad (Líneas 66-68)
```python
df_processed = crearRangosEdad(df_filtered)
```
**Ubicación**: Líneas 66-68  
**Propósito**: Ejecuta la función de categorización sobre los datos filtrados.

### FUNCIÓN 6: Limpiar datos nulos y estandarizar formato temporal (Líneas 70-77)
```python
df_processed = df_processed.dropna(subset=['Value', 'Time'])
df_processed['Year'] = pd.to_numeric(df_processed['Time'], errors='coerce')
df_processed = df_processed.dropna(subset=['Year'])
```
**Ubicación**: Líneas 70-77  
**Propósito**: Elimina registros con valores nulos en columnas críticas y convierte la columna Time a formato numérico.

### FUNCIÓN 7: Extraer valores únicos para filtros (Líneas 79-83)
```python
anios = sorted(df_processed['Year'].unique())
paises = ['Todos'] + sorted(df_processed['Location'].dropna().unique())
sexos = sorted(df_processed['Sex'].dropna().unique())
```
**Ubicación**: Líneas 79-83  
**Propósito**: Crea listas de valores únicos que serán usados en los filtros interactivos del dashboard.

### FUNCIÓN 8: Mostrar resumen estadístico (Líneas 85-88)
```python
print(f"Años disponibles: {min(anios)} - {max(anios)}")
print(f"Países disponibles: {len(paises)-1}")
print(f"Datos procesados: {len(df_processed)} registros")
```
**Ubicación**: Líneas 85-88  
**Propósito**: Proporciona información sobre el rango temporal y cobertura geográfica de los datos.

### FUNCIÓN 9: Preparar datos para embeber en HTML (Líneas 110-128)
```python
data_json = df_processed.to_json(orient="records")
paises_unicos = sorted(df_processed['Location'].dropna().unique().tolist())
anios_unicos = sorted(df_processed['Year'].dropna().unique().tolist())
total_registros = len(df_processed)
anio_minimo = min(anios)
anio_maximo = max(anios)
num_paises = len(paises) - 1
```
**Ubicación**: Líneas 110-128  
**Propósito**: Prepara los datos procesados y constantes para ser embebidos directamente en el HTML del dashboard, evitando archivos externos.

### FUNCIÓN 10: Generar estructura HTML completa (Líneas 130-1520)
```python
html_final = """
<!DOCTYPE html>
<html lang="es">
...
"""
```
**Ubicación**: Líneas 130-1520  
**Propósito**: Crea un dashboard web completo con HTML, CSS y JavaScript embebido.

---

## Datos Embebidos en HTML

### SECCIÓN 1: Datos principales embebidos (Líneas 1013-1022)
**Ubicación**: Líneas 1013-1022  
**Elemento**: `const globalData = """ + data_json + """;`  
**Propósito**: Embebe los datos poblacionales procesados directamente en el HTML como una constante JavaScript.

### SECCIÓN 2: Constantes calculadas embebidas (Líneas 1015-1021)
```javascript
const PAISES_DISPONIBLES = [lista de países];
const ANIOS_DISPONIBLES = [lista de años];
const POBLACION_TOTAL_2024 = 'población formateada';
const TOTAL_REGISTROS = número de registros;
const ANIO_MINIMO = año mínimo;
const ANIO_MAXIMO = año máximo;
const NUM_PAISES = número de países;
```
**Ubicación**: Líneas 1015-1021  
**Propósito**: Define constantes JavaScript con valores calculados desde Python para uso en el dashboard.

### SECCIÓN 3: Logs de verificación embebidos (Líneas 1023-1026)
```javascript
console.log('Datos embebidos cargados:', globalData.length, 'registros');
console.log('Países disponibles:', PAISES_DISPONIBLES.length);
console.log('Años disponibles:', ANIOS_DISPONIBLES.length);
console.log('Ejemplo de datos:', globalData[0]);
```
**Ubicación**: Líneas 1023-1026  
**Propósito**: Proporciona logs en la consola del navegador para verificar que los datos se cargaron correctamente.

### SECCIÓN 4: Inicialización automática (Líneas 1028-1031)
```javascript
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});
```
**Ubicación**: Líneas 1028-1031  
**Propósito**: Inicializa automáticamente el dashboard cuando la página termina de cargar, usando los datos embebidos.

---

## Funciones JavaScript del Dashboard

### Función: initializeDashboard() (Líneas 1033-1042)
**Ubicación**: Líneas 1033-1042  
**Propósito**: Inicializa el dashboard usando los datos embebidos y establece los event listeners para los controles interactivos.

### Función: updateCharts() (Líneas 1165-1182)
**Ubicación**: Líneas 1165-1182  
**Propósito**: Actualiza todos los gráficos del dashboard basándose en los filtros seleccionados, utilizando los datos embebidos.

### Función: updatePyramidChart() (Líneas 1189-1249)
**Ubicación**: Líneas 1189-1249  
**Propósito**: Actualiza el gráfico de pirámide poblacional separando hombres y mujeres.

### Función: updatePieChart() (Líneas 1255-1311)
**Ubicación**: Líneas 1255-1311  
**Propósito**: Actualiza el gráfico circular de distribución por categorías de edad.

### Función: updateTrendChart1() (Líneas 1308-1357)
**Ubicación**: Líneas 1308-1357  
**Propósito**: Actualiza el gráfico de tendencia temporal por categorías de edad.

### Función: updateTrendChart2() (Líneas 1363-1414)
**Ubicación**: Líneas 1363-1414  
**Propósito**: Actualiza el gráfico de tendencia porcentual por categorías.

### Función: updateVariationChart1() (Líneas 1420-1476)
**Ubicación**: Líneas 1420-1476  
**Propósito**: Actualiza el gráfico de variación poblacional por rangos de edad específicos.

### Función: updateVariationChart2() (Líneas 1482-1538)
**Ubicación**: Líneas 1482-1538  
**Propósito**: Actualiza el gráfico de variación poblacional por categorías amplias.

### Función: updateMetrics() (Líneas 1540-1551)
**Ubicación**: Líneas 1540-1551  
**Propósito**: Actualiza las métricas mostradas en el dashboard.

### Función: updateDualRange() (Líneas 1081-1115)
**Ubicación**: Líneas 1081-1115  
**Propósito**: Controla el slider dual para selección de rango de años.

---

## Filtros y Deslizadores

### FILTRO 1: Selector de país/región (Líneas 648-653)
**Ubicación**: Líneas 648-653  
**Elemento HTML**: `<select id="regionFilter">`  
**Propósito**: Permite filtrar datos por un país específico o ver datos globales. Afecta a TODOS los gráficos del dashboard.

### FILTRO 2: Deslizador de año individual (Líneas 655-672)
**Ubicación**: Líneas 655-672  
**Elemento HTML**: `<input type="range" id="yearSlider">`  
**Rango**: 1990-2025  
**Propósito**: Permite seleccionar un año específico para análisis puntual. Afecta a: Pirámide poblacional, gráfico circular y métrica de población total.

### FILTRO 3: Deslizador de rango de años (Líneas 722-733)
**Ubicación**: Líneas 722-733  
**Elementos HTML**: `<input type="range" id="rangeStart">` y `<input type="range" id="rangeEnd">`  
**Rango**: 1990-2025  
**Propósito**: Permite seleccionar dos años diferentes para comparar cambios poblacionales. Afecta a: Gráficos de variación poblacional (gráficos 5 y 6).

---

## Gráficos

### GRÁFICO 1: Pirámide de población (Líneas 685-690)
**Ubicación**: Líneas 685-690  
**Elemento HTML**: `<div id="pyramidChart">`  
**Propósito**: Muestra la distribución poblacional por edad y género en forma de pirámide.

### GRÁFICO 2: Distribución por categorías (Líneas 692-697)
**Ubicación**: Líneas 692-697  
**Elemento HTML**: `<div id="pieChart">`  
**Propósito**: Muestra la distribución porcentual de la población por rangos de edad.

### GRÁFICO 3: Tendencia temporal (Líneas 712-717)
**Ubicación**: Líneas 712-717  
**Elemento HTML**: `<div id="trendChart1">`  
**Propósito**: Muestra la tendencia de la población por categorías de edad a lo largo del tiempo.

### GRÁFICO 4: Tendencia porcentual (Líneas 719-724)
**Ubicación**: Líneas 719-724  
**Elemento HTML**: `<div id="trendChart2">`  
**Propósito**: Muestra la tendencia porcentual de la población por categorías.

### GRÁFICO 5: Variación por rangos (Líneas 746-751)
**Ubicación**: Líneas 746-751  
**Elemento HTML**: `<div id="variationChart1">`  
**Propósito**: Muestra la variación poblacional por rangos de edad específicos entre dos años.

### GRÁFICO 6: Variación por categorías (Líneas 753-758)
**Ubicación**: Líneas 753-758  
**Elemento HTML**: `<div id="variationChart2">`  
**Propósito**: Muestra la variación poblacional por categorías amplias entre dos años.

---

## Funciones de Utilidad

### updateSliderDisplay() (Líneas 1128-1136)
**Ubicación**: Líneas 1128-1136  
**Propósito**: Actualiza la visualización de los valores de los deslizadores.

### updateSliderProgress() (Líneas 1139-1151)
**Ubicación**: Líneas 1139-1151  
**Propósito**: Actualiza la barra de progreso visual de los deslizadores.

### animateValueChange() (Líneas 1117-1125)
**Ubicación**: Líneas 1117-1125  
**Propósito**: Proporciona animaciones visuales cuando cambian los valores de los controles.

---

## Archivo de Salida

### dashboard_poblacion.html (Líneas 1553-1571)
**Ubicación**: Líneas 1553-1571  
**Propósito**: Archivo HTML final que contiene el dashboard interactivo completo generado por el código Python, incluyendo todos los datos embebidos directamente en el HTML.

---

## Ventajas de los Datos Embebidos

### 1. **Portabilidad Completa**
- El archivo HTML generado es completamente autónomo
- No requiere archivos externos (JSON, CSS, JS separados)
- Funciona sin servidor web, directamente desde el navegador

### 2. **Rendimiento Optimizado**
- Los datos se cargan instantáneamente al abrir la página
- No hay latencia de red para cargar archivos externos
- Inicialización más rápida del dashboard

### 3. **Simplicidad de Distribución**
- Un solo archivo HTML contiene todo el dashboard
- Fácil de compartir, enviar por email o subir a cualquier hosting
- No hay dependencias de rutas relativas o archivos perdidos

### 4. **Seguridad Mejorada**
- No hay solicitudes HTTP externas que puedan fallar
- Los datos están protegidos dentro del archivo HTML
- Funciona offline sin problemas

---

## Resumen de Arquitectura

El código sigue una estructura modular dividida en:

1. **Procesamiento de datos** (Líneas 1-128): 
   - Carga, limpieza y preparación de datos
   - Generación de constantes y variables para embeber
   - Formateo de datos para integración directa en HTML

2. **Generación HTML con datos embebidos** (Líneas 130-1520): 
   - Creación del dashboard web completo
   - Embebido directo de datos JSON en JavaScript
   - Integración de constantes calculadas desde Python
   - CSS y JavaScript completamente integrados

3. **Funciones JavaScript con datos internos** (Líneas 1033-1551): 
   - Interactividad usando datos embebidos (sin archivos externos)
   - Actualización de gráficos con acceso directo a datos
   - Control de filtros y deslizadores
   - Inicialización automática con datos precargados

4. **Guardado de archivo único** (Líneas 1553-1571): 
   - Exportación del dashboard como archivo HTML autónomo
   - Inclusion completa de datos, estilos y funcionalidad
   - Sin dependencias externas

### Flujo de Datos Embebidos:
```
Python DataFrame → JSON String → HTML Template → JavaScript Const → Plotly Charts
```

El dashboard resultante es completamente autónomo, portable y permite analizar datos poblacionales de múltiples maneras sin requerir archivos externos, servidores web o conexión a internet.
