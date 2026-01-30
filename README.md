# ⚡ Energy Advisor - Backend con IA

Sistema inteligente de recomendaciones para ahorro energético usando datos climáticos de Open-Meteo y análisis con Gemini AI.

## 🌟 Características

- ✅ **Análisis climático** para múltiples zonas de México
- ✅ **Sugerencias personalizadas con IA** (Gemini 1.5 Flash)
- ✅ **Métricas energéticas** (CDD, potencial solar, días críticos)
- ✅ **Gráficas automáticas** (temperatura y radiación solar)
- ✅ **Exportación a CSV** de datos climáticos
- ✅ **API REST** lista para integración web
- ✅ **Frontend de ejemplo** incluido

## 📋 Requisitos Previos

- Python 3.8 o superior
- Cuenta gratuita de Google AI (para Gemini API)

## 🚀 Instalación Rápida

### 1. Clonar/Descargar el Proyecto

```bash
# Si usas Git
git clone https://github.com/tu-usuario/energy-advisor.git
cd energy-advisor

# O simplemente descarga los archivos y extráelos
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar API Key de Gemini

**Paso a paso para obtener tu API Key GRATIS:**

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Create API Key"
4. Copia la clave generada

**Configurar la clave:**

```bash
# Opción 1: Variable de entorno (recomendado)
export GEMINI_API_KEY="tu-api-key-aqui"

# Opción 2: Archivo .env
cp .env.example .env
# Edita .env y pega tu API key
```

### 5. Ejecutar el Servidor

```bash
python energy_advisor_backend.py
```

El servidor estará disponible en: **http://localhost:5000**

## 🎯 Uso Básico

### Opción 1: Frontend Incluido

1. Abre `frontend_example.html` en tu navegador
2. Selecciona tipo de usuario, zona y días
3. Haz clic en "Analizar"
4. ¡Disfruta de tu sugerencia personalizada!

### Opción 2: API REST Directa

**Ejemplo con cURL:**

```bash
curl -X POST http://localhost:5000/api/analizar \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_usuario": "hogar",
    "zona": "monterrey",
    "dias": 30
  }'
```

**Ejemplo con Python:**

```python
import requests

response = requests.post('http://localhost:5000/api/analizar', json={
    'tipo_usuario': 'hogar',
    'zona': 'monterrey',
    'dias': 30
})

data = response.json()
print(data['sugerencia'])
```

**Ejemplo con JavaScript:**

```javascript
fetch('http://localhost:5000/api/analizar', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tipo_usuario: 'industria',
    zona: 'guadalajara',
    dias: 60
  })
})
.then(res => res.json())
.then(data => console.log(data.sugerencia));
```

## 📚 Documentación de la API

Ver [API_DOCS.md](API_DOCS.md) para documentación completa de todos los endpoints.

### Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health` | GET | Verificar estado del servidor |
| `/api/zonas` | GET | Listar zonas disponibles |
| `/api/analizar` | POST | Análisis completo con IA |
| `/api/exportar-csv` | POST | Exportar datos a CSV |

## 🗺️ Zonas Disponibles

- **Monterrey, NL** - Zona industrial del norte
- **Guadalajara, JAL** - Zona metropolitana centro-occidente
- **Ciudad de México** - Megalópolis del centro
- **Tijuana, BC** - Frontera noroeste
- **Cancún, QR** - Zona turística caribeña

## 📊 Ejemplo de Respuesta

```json
{
  "exito": true,
  "metricas": {
    "temp_promedio": 25.3,
    "temp_maxima": 38.5,
    "dias_calor_extremo": 12,
    "potencial_solar_promedio": 18.2,
    "dias_optimos_solar": 25
  },
  "sugerencia": "### OPTIMIZA TU AIRE ACONDICIONADO\n\nCon 12 días proyectados...",
  "graficas": {
    "temperatura": "base64_image...",
    "solar": "base64_image..."
  }
}
```

## 🛠️ Estructura del Proyecto

```
energy-advisor/
├── energy_advisor_backend.py    # Backend principal
├── frontend_example.html        # Ejemplo de frontend
├── requirements.txt             # Dependencias
├── .env.example                 # Template de configuración
├── API_DOCS.md                  # Documentación completa
└── README.md                    # Este archivo
```

## 🔧 Personalización

### Agregar Nuevas Zonas

Edita el diccionario `COORDENADAS_ZONAS` en `energy_advisor_backend.py`:

```python
COORDENADAS_ZONAS = {
    "tu_ciudad": {
        "lat": 19.4326,
        "lon": -99.1332,
        "tz": "America/Mexico_City"
    }
}
```

### Modificar Umbrales

```python
TEMP_CONFORT = 24    # Temperatura de confort (°C)
TEMP_EXTREMO = 35    # Temperatura extrema (°C)
```

### Cambiar Modelo de IA

```python
# En la configuración de Gemini
model = genai.GenerativeModel('gemini-1.5-pro')  # Modelo más potente
```

## 🐛 Solución de Problemas

### Error: "GEMINI_API_KEY no configurada"

**Solución:**
```bash
export GEMINI_API_KEY="tu-clave-aqui"
```

### Error: "ModuleNotFoundError"

**Solución:**
```bash
pip install -r requirements.txt --upgrade
```

### Error: "Connection refused"

**Solución:**
- Verifica que el backend esté corriendo en `localhost:5000`
- Revisa el firewall o antivirus

### Error: "CORS policy"

**Solución:** El backend ya tiene CORS habilitado. Si persiste:
```python
# En energy_advisor_backend.py, modifica:
CORS(app, origins=["http://tu-dominio.com"])
```

## 📈 Límites de Uso (Gemini Free Tier)

- **15 peticiones por minuto**
- **1,500 peticiones por día**
- Suficiente para proyectos pequeños/medianos

Para más peticiones: [Gemini Pricing](https://ai.google.dev/pricing)

## 🚀 Despliegue en Producción

### Heroku

```bash
# Crear Procfile
echo "web: python energy_advisor_backend.py" > Procfile

# Desplegar
heroku create mi-energy-advisor
heroku config:set GEMINI_API_KEY=tu-clave
git push heroku main
```

### Railway

1. Conecta tu repositorio en [railway.app](https://railway.app)
2. Añade variable de entorno `GEMINI_API_KEY`
3. ¡Despliega automáticamente!

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "energy_advisor_backend.py"]
```

```bash
docker build -t energy-advisor .
docker run -p 5000:5000 -e GEMINI_API_KEY=tu-clave energy-advisor
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📝 Licencia

Este proyecto es de código abierto bajo la licencia MIT.

## 👨‍💻 Autor

Desarrollado para el proyecto de ahorro energético con datos climáticos.

## 📞 Soporte

Si tienes problemas:

1. Revisa la [documentación de la API](API_DOCS.md)
2. Verifica los [problemas comunes](#-solución-de-problemas)
3. Crea un issue en el repositorio

---

## 🎓 Aprendizaje Adicional

### APIs Usadas

- **Open-Meteo Climate API**: [Documentación](https://open-meteo.com/en/docs/climate-api)
- **Gemini API**: [Documentación](https://ai.google.dev/docs)

### Tecnologías

- **Flask**: Framework web de Python
- **Pandas**: Análisis de datos
- **Matplotlib**: Visualización
- **Google Generative AI**: Modelos de lenguaje

---

**¡Ahorra energía de forma inteligente!** ⚡🌍
