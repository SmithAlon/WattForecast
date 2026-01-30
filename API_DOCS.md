# 📘 Documentación de la API - Energy Advisor

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar o descargar los archivos
cd energy-advisor-backend

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar .env y añadir tu GEMINI_API_KEY
# Obtener key gratis en: https://makersuite.google.com/app/apikey
```

### 3. Ejecutar Servidor

```bash
python energy_advisor_backend.py
```

El servidor estará disponible en: `http://localhost:5000`

---

## 📋 Endpoints Disponibles

### 1. Health Check

Verifica que el servidor está funcionando.

**Endpoint:** `GET /api/health`

**Respuesta:**
```json
{
  "status": "ok",
  "message": "Backend de Energy Advisor activo",
  "timestamp": "2025-02-08T10:30:00"
}
```

**Ejemplo cURL:**
```bash
curl http://localhost:5000/api/health
```

---

### 2. Obtener Zonas Disponibles

Lista todas las zonas disponibles para análisis.

**Endpoint:** `GET /api/zonas`

**Respuesta:**
```json
{
  "zonas": [
    {"id": "monterrey", "nombre": "Monterrey"},
    {"id": "guadalajara", "nombre": "Guadalajara"},
    {"id": "cdmx", "nombre": "Cdmx"},
    {"id": "tijuana", "nombre": "Tijuana"},
    {"id": "cancun", "nombre": "Cancun"}
  ]
}
```

**Ejemplo cURL:**
```bash
curl http://localhost:5000/api/zonas
```

---

### 3. Análisis Completo (Endpoint Principal)

Genera análisis climático, métricas energéticas, sugerencia IA y gráficas.

**Endpoint:** `POST /api/analizar`

**Body (JSON):**
```json
{
  "tipo_usuario": "hogar",
  "zona": "monterrey",
  "dias": 30
}
```

**Parámetros:**
- `tipo_usuario` (string, requerido): `"hogar"` o `"industria"`
- `zona` (string, requerido): Una de las zonas disponibles
- `dias` (integer, requerido): Entre 7 y 365

**Respuesta Exitosa (200):**
```json
{
  "exito": true,
  "timestamp": "2025-02-08T10:30:00",
  "parametros": {
    "tipo_usuario": "hogar",
    "zona": "monterrey",
    "dias": 30
  },
  "metricas": {
    "temp_promedio": 22.5,
    "temp_maxima": 35.2,
    "temp_minima": 10.3,
    "cdd_total": 180.5,
    "dias_calor_extremo": 8,
    "dias_confortables": 5,
    "radiacion_promedio": 20.3,
    "potencial_solar_promedio": 15.8,
    "dias_optimos_solar": 22,
    "humedad_promedio": 55.2,
    "dias_demanda_alta": 12
  },
  "sugerencia": "### INSTALA TERMOSTATO PROGRAMABLE INTELIGENTE\n\n**Análisis:**\nCon 8 días proyectados...",
  "graficas": {
    "temperatura": "base64_encoded_image...",
    "solar": "base64_encoded_image..."
  }
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:5000/api/analizar \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_usuario": "hogar",
    "zona": "monterrey",
    "dias": 30
  }'
```

**Ejemplo JavaScript (Fetch):**
```javascript
fetch('http://localhost:5000/api/analizar', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tipo_usuario: 'hogar',
    zona: 'monterrey',
    dias: 30
  })
})
.then(response => response.json())
.then(data => {
  console.log('Sugerencia:', data.sugerencia);
  console.log('Métricas:', data.metricas);
  
  // Mostrar gráficas
  document.getElementById('grafica-temp').src = 
    `data:image/png;base64,${data.graficas.temperatura}`;
  document.getElementById('grafica-solar').src = 
    `data:image/png;base64,${data.graficas.solar}`;
});
```

**Ejemplo Python (requests):**
```python
import requests

response = requests.post('http://localhost:5000/api/analizar', json={
    'tipo_usuario': 'industria',
    'zona': 'guadalajara',
    'dias': 60
})

data = response.json()
print(data['sugerencia'])
```

---

### 4. Exportar CSV

Descarga los datos climáticos en formato CSV.

**Endpoint:** `POST /api/exportar-csv`

**Body (JSON):**
```json
{
  "zona": "monterrey",
  "dias": 30
}
```

**Respuesta:** Archivo CSV descargable

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:5000/api/exportar-csv \
  -H "Content-Type: application/json" \
  -d '{"zona": "monterrey", "dias": 30}' \
  -o datos_climaticos.csv
```

**Ejemplo JavaScript (descarga en frontend):**
```javascript
fetch('http://localhost:5000/api/exportar-csv', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    zona: 'monterrey',
    dias: 30
  })
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'datos_climaticos.csv';
  a.click();
});
```

---

## 🎨 Ejemplo Completo de Integración Frontend

### HTML + JavaScript Vanilla

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Energy Advisor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .form-group {
            margin: 15px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        select, input {
            padding: 10px;
            font-size: 16px;
            width: 100%;
            max-width: 300px;
        }
        button {
            padding: 12px 30px;
            font-size: 16px;
            background: #3498db;
            color: white;
            border: none;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #2980b9;
        }
        .resultado {
            margin-top: 30px;
            padding: 20px;
            background: #f4f4f4;
            border-radius: 5px;
        }
        .graficas {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        .graficas img {
            width: 100%;
            border-radius: 5px;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>🌟 Energy Advisor - Ahorro Energético Inteligente</h1>
    
    <form id="formulario">
        <div class="form-group">
            <label>Tipo de Usuario:</label>
            <select id="tipo_usuario">
                <option value="hogar">🏠 Hogar</option>
                <option value="industria">🏭 Industria</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>Zona:</label>
            <select id="zona">
                <option value="monterrey">Monterrey</option>
                <option value="guadalajara">Guadalajara</option>
                <option value="cdmx">Ciudad de México</option>
                <option value="tijuana">Tijuana</option>
                <option value="cancun">Cancún</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>Días a Proyectar (7-365):</label>
            <input type="number" id="dias" value="30" min="7" max="365">
        </div>
        
        <button type="submit">🔍 Analizar</button>
        <button type="button" id="btnExportar" style="background: #27ae60;">
            📥 Exportar CSV
        </button>
    </form>
    
    <div class="loading" id="loading">
        <h3>⏳ Analizando datos climáticos y generando sugerencia...</h3>
    </div>
    
    <div id="resultado" class="resultado" style="display: none;">
        <h2>📊 Resultados del Análisis</h2>
        
        <div id="metricas">
            <!-- Métricas se insertan aquí -->
        </div>
        
        <div id="sugerencia" style="margin-top: 20px; padding: 20px; background: white; border-left: 5px solid #3498db;">
            <!-- Sugerencia IA se inserta aquí -->
        </div>
        
        <div class="graficas">
            <div>
                <h3>🌡️ Perfil Térmico</h3>
                <img id="grafica-temp" alt="Gráfica de temperatura">
            </div>
            <div>
                <h3>☀️ Potencial Solar</h3>
                <img id="grafica-solar" alt="Gráfica solar">
            </div>
        </div>
    </div>
    
    <script>
        const API_URL = 'http://localhost:5000';
        
        document.getElementById('formulario').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const tipo = document.getElementById('tipo_usuario').value;
            const zona = document.getElementById('zona').value;
            const dias = parseInt(document.getElementById('dias').value);
            
            // Mostrar loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('resultado').style.display = 'none';
            
            try {
                const response = await fetch(`${API_URL}/api/analizar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tipo_usuario: tipo, zona, dias })
                });
                
                const data = await response.json();
                
                if (data.exito) {
                    // Mostrar métricas
                    const m = data.metricas;
                    document.getElementById('metricas').innerHTML = `
                        <h3>📈 Métricas Climáticas</h3>
                        <p><strong>Temperatura Promedio:</strong> ${m.temp_promedio}°C</p>
                        <p><strong>Temperatura Máxima:</strong> ${m.temp_maxima}°C</p>
                        <p><strong>Días de Calor Extremo:</strong> ${m.dias_calor_extremo}</p>
                        <p><strong>Potencial Solar:</strong> ${m.potencial_solar_promedio} MJ/m²</p>
                        <p><strong>Días Óptimos para Solar:</strong> ${m.dias_optimos_solar}</p>
                    `;
                    
                    // Mostrar sugerencia (preservar formato Markdown)
                    document.getElementById('sugerencia').innerHTML = 
                        `<h3>💡 Sugerencia Personalizada</h3>
                         <pre style="white-space: pre-wrap; font-family: inherit;">${data.sugerencia}</pre>`;
                    
                    // Mostrar gráficas
                    document.getElementById('grafica-temp').src = 
                        `data:image/png;base64,${data.graficas.temperatura}`;
                    document.getElementById('grafica-solar').src = 
                        `data:image/png;base64,${data.graficas.solar}`;
                    
                    document.getElementById('resultado').style.display = 'block';
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error de conexión: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        });
        
        // Botón exportar CSV
        document.getElementById('btnExportar').addEventListener('click', async () => {
            const zona = document.getElementById('zona').value;
            const dias = parseInt(document.getElementById('dias').value);
            
            try {
                const response = await fetch(`${API_URL}/api/exportar-csv`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ zona, dias })
                });
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `datos_${zona}_${dias}dias.csv`;
                a.click();
            } catch (error) {
                alert('Error al exportar: ' + error.message);
            }
        });
    </script>
</body>
</html>
```

---

## 🔧 Códigos de Error

| Código | Descripción |
|--------|-------------|
| 400 | Parámetros inválidos |
| 500 | Error interno del servidor |

---

## 📊 Estructura de Métricas

Las métricas retornadas incluyen:

- **temp_promedio**: Temperatura promedio del periodo (°C)
- **temp_maxima**: Temperatura máxima esperada (°C)
- **temp_minima**: Temperatura mínima esperada (°C)
- **cdd_total**: Grados-Día de Enfriamiento (predictor de uso de AC)
- **dias_calor_extremo**: Días con temperatura > 35°C
- **dias_confortables**: Días con temperatura < 24°C
- **radiacion_promedio**: Radiación solar promedio (MJ/m²)
- **potencial_solar_promedio**: Energía solar efectiva considerando nubosidad
- **dias_optimos_solar**: Días con nubosidad < 40%
- **humedad_promedio**: Humedad relativa promedio (%)
- **dias_demanda_alta**: Días con calor + humedad alta

---

## 🚀 Despliegue en Producción

### Opción 1: Heroku

```bash
# Crear Procfile
echo "web: python energy_advisor_backend.py" > Procfile

# Desplegar
heroku create energy-advisor-api
git push heroku main
```

### Opción 2: Railway

```bash
# Configurar en railway.app
# Variables de entorno: GEMINI_API_KEY
```

### Opción 3: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "energy_advisor_backend.py"]
```

---

## 📝 Notas Importantes

1. **API Key de Gemini**: Es gratuita pero tiene límites de uso (15 req/min)
2. **Cache**: El sistema cachea 100 consultas recientes para optimizar
3. **CORS**: Habilitado para todos los orígenes (ajustar en producción)
4. **Rate Limiting**: Considera añadir Flask-Limiter en producción

---

## 🆘 Soporte

Si encuentras problemas:
1. Verifica que tu `GEMINI_API_KEY` es válida
2. Confirma que todas las dependencias están instaladas
3. Revisa los logs del servidor para errores específicos

**¡Listo para empezar!** 🚀
