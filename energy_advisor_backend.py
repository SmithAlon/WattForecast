"""
BACKEND - Sistema de Recomendaciones Energéticas
Integración: Open-Meteo API + Gemini AI
Autor: Adaptado para proyecto web
"""

from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
load_dotenv()
from flask_cors import CORS
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend sin interfaz gráfica para servidor
import matplotlib.pyplot as plt
import google.generativeai as genai
from datetime import datetime, timedelta
import io
import base64
import os
from functools import lru_cache

# ==========================================
# CONFIGURACIÓN DEL SERVIDOR
# ==========================================
app = Flask(__name__)
CORS(app)  # Permitir peticiones desde frontend

# Configurar Gemini (¡IMPORTANTE! Obtén tu key en https://aistudio.google.com/app/apikey)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "TU_API_KEY_AQUÍ")
genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# CONSTANTES Y CONFIGURACIÓN
# ==========================================
COORDENADAS_ZONAS = {
    "monterrey": {"lat": 25.6866, "lon": -100.3161, "tz": "America/Monterrey"},
    "guadalajara": {"lat": 20.6597, "lon": -103.3496, "tz": "America/Mexico_City"},
    "cdmx": {"lat": 19.4326, "lon": -99.1332, "tz": "America/Mexico_City"},
    "tijuana": {"lat": 32.5149, "lon": -117.0382, "tz": "America/Tijuana"},
    "cancun": {"lat": 21.1619, "lon": -86.8515, "tz": "America/Cancun"}
}

# Timezone por defecto para zonas personalizadas
DEFAULT_TIMEZONE = "auto"

# Umbrales de confort térmico
TEMP_CONFORT = 24  # °C
TEMP_EXTREMO = 35  # °C

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

@lru_cache(maxsize=100)
def obtener_datos_climaticos(zona, dias_adelante, lat=None, lon=None, tz=None):
    """
    Consulta la API de Open-Meteo y retorna DataFrame con datos climáticos
    Cache de 100 consultas recientes para optimizar
    
    Args:
        zona: Nombre de la zona (puede ser predefinida o personalizada)
        dias_adelante: Número de días a proyectar
        lat: Latitud (opcional, para zonas personalizadas)
        lon: Longitud (opcional, para zonas personalizadas)
        tz: Timezone (opcional, para zonas personalizadas)
    """
    # Si se proporcionan coordenadas directamente, usarlas
    if lat is not None and lon is not None:
        coords = {"lat": lat, "lon": lon, "tz": tz or DEFAULT_TIMEZONE}
    elif zona.lower() in COORDENADAS_ZONAS:
        coords = COORDENADAS_ZONAS[zona.lower()]
    else:
        raise ValueError(f"Zona '{zona}' no disponible y no se proporcionaron coordenadas.")
    
    # Calcular fechas
    fecha_inicio = datetime.now().strftime("%Y-%m-%d")
    fecha_fin = (datetime.now() + timedelta(days=dias_adelante)).strftime("%Y-%m-%d")
    
    # Parámetros para la API
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "start_date": fecha_inicio,
        "end_date": fecha_fin,
        "models": "MRI_AGCM3_2_S",
        "daily": [
            "temperature_2m_mean",
            "temperature_2m_max",
            "relative_humidity_2m_mean",
            "shortwave_radiation_sum",
            "cloud_cover_mean",
            "wind_speed_10m_mean"
        ],
        "timezone": coords["tz"]
    }
    
    # Petición a la API
    response = requests.get("https://climate-api.open-meteo.com/v1/climate", params=params)
    response.raise_for_status()
    data = response.json()
    
    # Convertir a DataFrame
    df = pd.DataFrame(data['daily'])
    df['time'] = pd.to_datetime(df['time'])
    
    # Renombrar columnas
    df.rename(columns={
        'time': 'Fecha',
        'temperature_2m_mean': 'Temp_Promedio',
        'temperature_2m_max': 'Temp_Maxima',
        'relative_humidity_2m_mean': 'Humedad_Relativa',
        'shortwave_radiation_sum': 'Radiacion_Solar',
        'cloud_cover_mean': 'Nubosidad',
        'wind_speed_10m_mean': 'Velocidad_Viento'
    }, inplace=True)
    
    return df


def calcular_metricas_energeticas(df):
    """
    Calcula indicadores clave para el análisis energético
    """
    metricas = {}
    
    # Temperatura
    metricas['temp_promedio'] = round(df['Temp_Promedio'].mean(), 1)
    metricas['temp_maxima'] = round(df['Temp_Maxima'].max(), 1)
    metricas['temp_minima'] = round(df['Temp_Promedio'].min(), 1)
    
    # Grados-Día de Enfriamiento (CDD) - Predictor de uso de AC
    df['CDD'] = (df['Temp_Promedio'] - TEMP_CONFORT).clip(lower=0)
    metricas['cdd_total'] = round(df['CDD'].sum(), 1)
    
    # Días críticos
    metricas['dias_calor_extremo'] = int((df['Temp_Maxima'] > TEMP_EXTREMO).sum())
    metricas['dias_confortables'] = int((df['Temp_Maxima'] <= TEMP_CONFORT).sum())
    
    # Potencial solar
    df['Potencial_Solar'] = df['Radiacion_Solar'] * (1 - df['Nubosidad']/100)
    metricas['radiacion_promedio'] = round(df['Radiacion_Solar'].mean(), 1)
    metricas['potencial_solar_promedio'] = round(df['Potencial_Solar'].mean(), 1)
    metricas['dias_optimos_solar'] = int((df['Nubosidad'] < 40).sum())
    
    # Humedad (factor de confort térmico)
    metricas['humedad_promedio'] = round(df['Humedad_Relativa'].mean(), 1)
    
    # Días con alta demanda energética (calor + humedad)
    metricas['dias_demanda_alta'] = int(
        ((df['Temp_Maxima'] > 32) & (df['Humedad_Relativa'] > 60)).sum()
    )
    
    return metricas


def generar_sugerencia_ia(metricas, tipo_usuario, zona, dias):
    """
    Genera sugerencia personalizada usando Gemini AI
    """
    
    # Contexto específico por tipo de usuario
    contexto_usuario = {
        "hogar": """
        Enfócate en acciones prácticas para familias:
        - Uso eficiente de aire acondicionado y ventiladores
        - Aprovechamiento de luz natural y ventilación
        - Consideración de paneles solares residenciales
        - Ajustes en horarios de uso de electrodomésticos
        """,
        "industria": """
        Enfócate en optimización industrial:
        - Desplazamiento de cargas a horarios valle
        - Mantenimiento predictivo de sistemas HVAC
        - Cogeneración y almacenamiento energético
        - Automatización de climatización por zonas
        """
    }
    
    prompt = f"""
Eres un asesor energético certificado en México. Analiza estos datos climáticos de {zona.title()} para los próximos {dias} días y genera UNA sugerencia de ahorro energético.

**TIPO DE USUARIO:** {tipo_usuario.upper()}
**ZONA:** {zona.title()}
**PERIODO:** {dias} días

**DATOS CLIMÁTICOS:**
- Temperatura promedio: {metricas['temp_promedio']}°C
- Temperatura máxima esperada: {metricas['temp_maxima']}°C
- Días con calor extremo (>35°C): {metricas['dias_calor_extremo']}
- Grados-día de enfriamiento (CDD): {metricas['cdd_total']}
- Radiación solar promedio: {metricas['radiacion_promedio']} MJ/m²
- Potencial solar efectivo: {metricas['potencial_solar_promedio']} MJ/m²
- Días óptimos para solar: {metricas['dias_optimos_solar']}
- Días con demanda alta: {metricas['dias_demanda_alta']}
- Humedad relativa promedio: {metricas['humedad_promedio']}%

{contexto_usuario[tipo_usuario]}

**FORMATO DE RESPUESTA (ESTRICTAMENTE):**

### [Título Impactante de la Sugerencia]

**Análisis:**
[2-3 oraciones vinculando los datos climáticos con el impacto energético específico]

**Acción Recomendada:**
[Descripción clara y específica de QUÉ hacer y CÓMO implementarlo]

**Ahorro Estimado:**
[Porcentaje o monto aproximado en MXN, con justificación basada en los datos]

**Prioridad:** [Alta/Media/Baja basada en impacto vs esfuerzo]

---
IMPORTANTE: 
- Máximo 200 palabras total
- Usa los datos numéricos proporcionados
- Sé específico con acciones medibles
- No inventes datos que no te di
"""
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error al generar sugerencia: {str(e)}\n\nSugerencia básica: Con las condiciones climáticas proyectadas, considera optimizar el uso de climatización en horarios pico."


def generar_graficas(df, zona):
    """
    Genera gráficas en formato base64 para enviar al frontend
    """
    plt.style.use('bmh')
    graficas = {}
    
    # GRÁFICA 1: Perfil Térmico
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    
    ax1.plot(df['Fecha'], df['Temp_Maxima'], 
             color='#E74C3C', alpha=0.7, linewidth=2, label='Temperatura Máxima')
    ax1.plot(df['Fecha'], df['Temp_Promedio'].rolling(7).mean(), 
             color='#C0392B', linestyle='--', linewidth=2, label='Tendencia (7 días)')
    
    ax1.axhline(y=TEMP_CONFORT, color='#27AE60', linestyle=':', linewidth=2, 
                label=f'Umbral Confort ({TEMP_CONFORT}°C)')
    ax1.axhline(y=TEMP_EXTREMO, color='#E67E22', linestyle=':', linewidth=2, 
                label=f'Calor Extremo ({TEMP_EXTREMO}°C)')
    
    ax1.fill_between(df['Fecha'], TEMP_CONFORT, df['Temp_Maxima'], 
                     where=(df['Temp_Maxima'] > TEMP_CONFORT), 
                     alpha=0.2, color='red', label='Zona de Alto Consumo AC')
    
    ax1.set_xlabel('Fecha', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Temperatura (°C)', fontsize=12, fontweight='bold')
    ax1.set_title(f'Perfil Térmico - {zona.title()}: Predicción de Demanda Energética', 
                  fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convertir a base64
    buffer1 = io.BytesIO()
    plt.savefig(buffer1, format='png', dpi=100, bbox_inches='tight')
    buffer1.seek(0)
    graficas['temperatura'] = base64.b64encode(buffer1.read()).decode()
    plt.close()
    
    # GRÁFICA 2: Potencial Solar
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    
    color_rad = '#F39C12'
    ax2.set_xlabel('Fecha', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Radiación Solar (MJ/m²)', color=color_rad, fontsize=12, fontweight='bold')
    ax2.plot(df['Fecha'], df['Radiacion_Solar'], 
             color=color_rad, linewidth=2, label='Radiación Solar Disponible')
    ax2.tick_params(axis='y', labelcolor=color_rad)
    
    # Eje secundario: Nubosidad
    ax3 = ax2.twinx()
    color_cloud = '#7F8C8D'
    ax3.set_ylabel('Nubosidad (%)', color=color_cloud, fontsize=12, fontweight='bold')
    ax3.fill_between(df['Fecha'], df['Nubosidad'], 
                     color=color_cloud, alpha=0.3, label='Cobertura de Nubes')
    ax3.tick_params(axis='y', labelcolor=color_cloud)
    
    plt.title(f'Potencial de Generación Solar - {zona.title()}', 
              fontsize=14, fontweight='bold')
    
    # Leyenda combinada
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax3.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buffer2 = io.BytesIO()
    plt.savefig(buffer2, format='png', dpi=100, bbox_inches='tight')
    buffer2.seek(0)
    graficas['solar'] = base64.b64encode(buffer2.read()).decode()
    plt.close()
    
    return graficas


# ==========================================
# ENDPOINTS DE LA API
# ==========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar que el servidor está funcionando"""
    return jsonify({
        "status": "ok",
        "message": "Backend de Energy Advisor activo",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/zonas', methods=['GET'])
def obtener_zonas():
    """Retorna las zonas disponibles"""
    zonas = [{"id": k, "nombre": k.title()} for k in COORDENADAS_ZONAS.keys()]
    return jsonify({"zonas": zonas})


@app.route('/api/geocode', methods=['GET'])
def geocode():
    """
    Busca ubicaciones por nombre usando la API de geocodificación de Open-Meteo
    
    Query params:
        q: Término de búsqueda (nombre de ciudad, dirección, etc.)
    """
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({"resultados": [], "error": "El término de búsqueda debe tener al menos 2 caracteres"}), 400
    
    try:
        # Usar API de geocodificación de Open-Meteo
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": query,
                "count": 10,
                "language": "es",
                "format": "json"
            }
        )
        response.raise_for_status()
        data = response.json()
        
        resultados = []
        if "results" in data:
            for r in data["results"]:
                resultados.append({
                    "nombre": r.get("name", ""),
                    "pais": r.get("country", ""),
                    "admin1": r.get("admin1", ""),  # Estado/Provincia
                    "lat": r.get("latitude"),
                    "lon": r.get("longitude"),
                    "tz": r.get("timezone", DEFAULT_TIMEZONE),
                    "display": f"{r.get('name', '')}, {r.get('admin1', '')} - {r.get('country', '')}"
                })
        
        return jsonify({"resultados": resultados})
    
    except Exception as e:
        return jsonify({"resultados": [], "error": str(e)}), 500


@app.route('/api/analizar', methods=['POST'])
def analizar():
    """
    Endpoint principal: Analiza datos climáticos y genera recomendación
    
    Body esperado (JSON):
    {
        "tipo_usuario": "hogar" o "industria",
        "zona": "monterrey" o nombre personalizado,
        "dias": 30,
        "lat": 25.6866,  // opcional: latitud para zona personalizada
        "lon": -100.3161,  // opcional: longitud para zona personalizada
        "tz": "America/Mexico_City"  // opcional: timezone
    }
    """
    try:
        # Validar datos de entrada
        data = request.json
        tipo_usuario = data.get('tipo_usuario', 'hogar').lower()
        zona = data.get('zona', 'monterrey')
        dias = int(data.get('dias', 30))
        
        # Coordenadas opcionales para zonas personalizadas
        lat = data.get('lat')
        lon = data.get('lon')
        tz = data.get('tz')
        
        if tipo_usuario not in ['hogar', 'industria']:
            return jsonify({"error": "tipo_usuario debe ser 'hogar' o 'industria'"}), 400
        
        # Validar que se proporcione zona predefinida o coordenadas
        zona_lower = zona.lower()
        if zona_lower not in COORDENADAS_ZONAS and (lat is None or lon is None):
            return jsonify({"error": f"Zona '{zona}' no es predefinida. Proporcione coordenadas (lat, lon) o busque una ubicación."}), 400
        
        if not 7 <= dias <= 365:
            return jsonify({"error": "El rango de días debe estar entre 7 y 365"}), 400
        
        # 1. Obtener datos climáticos
        df = obtener_datos_climaticos(zona, dias, lat, lon, tz)
        
        # 2. Calcular métricas
        metricas = calcular_metricas_energeticas(df)
        
        # 3. Generar sugerencia con IA
        sugerencia = generar_sugerencia_ia(metricas, tipo_usuario, zona, dias)
        
        # 4. Generar gráficas
        graficas = generar_graficas(df, zona)
        
        # 5. Preparar respuesta
        respuesta = {
            "exito": True,
            "timestamp": datetime.now().isoformat(),
            "parametros": {
                "tipo_usuario": tipo_usuario,
                "zona": zona,
                "dias": dias
            },
            "metricas": metricas,
            "sugerencia": sugerencia,
            "graficas": {
                "temperatura": graficas['temperatura'],
                "solar": graficas['solar']
            }
        }
        
        return jsonify(respuesta)
    
    except Exception as e:
        return jsonify({
            "exito": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/exportar-csv', methods=['POST'])
def exportar_csv():
    """
    Genera y descarga CSV con los datos climáticos
    
    Body esperado (JSON):
    {
        "zona": "monterrey",
        "dias": 30,
        "lat": 25.6866,  // opcional
        "lon": -100.3161,  // opcional
        "tz": "America/Mexico_City"  // opcional
    }
    """
    try:
        data = request.json
        zona = data.get('zona', 'monterrey')
        dias = int(data.get('dias', 30))
        lat = data.get('lat')
        lon = data.get('lon')
        tz = data.get('tz')
        
        # Obtener datos
        df = obtener_datos_climaticos(zona, dias, lat, lon, tz)
        
        # Convertir a CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Retornar como archivo descargable
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'datos_climaticos_{zona}_{dias}dias_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    except Exception as e:
        return jsonify({
            "exito": False,
            "error": str(e)
        }), 500


# ==========================================
# EJECUTAR SERVIDOR
# ==========================================
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Energy Advisor Backend - Iniciando servidor...")
    print("=" * 60)
    print(f"📍 Zonas predefinidas: {list(COORDENADAS_ZONAS.keys())}")
    print(f"🌍 Búsqueda global de ubicaciones: HABILITADA")
    print(f"🤖 Modelo IA: Gemini 2.0 Flash")
    print(f"🌐 API Climate: Open-Meteo")
    print("=" * 60)
    
    # Verificar API key
    if GEMINI_API_KEY == "TU_API_KEY_AQUÍ":
        print("⚠️  WARNING: Configura tu GEMINI_API_KEY antes de producción!")
        print("   Obtén tu key gratis en: https://makersuite.google.com/app/apikey")
        print("=" * 60)
    
    # Modo desarrollo
    app.run(debug=True, host='0.0.0.0', port=5000)
