"""
Script de Testing - Energy Advisor Backend
Prueba todos los endpoints de la API
"""

import requests
import json
import time

# Configuración
API_URL = "http://localhost:5000"

def print_section(title):
    """Imprime un separador visual"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test 1: Verificar que el servidor está activo"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_URL}/api/health")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200, "El servidor no está respondiendo"
        assert data['status'] == 'ok', "El servidor no está OK"
        
        print("✅ PASÓ - Servidor activo")
        return True
        
    except Exception as e:
        print(f"❌ FALLÓ - {str(e)}")
        return False

def test_zonas():
    """Test 2: Obtener zonas disponibles"""
    print_section("TEST 2: Obtener Zonas")
    
    try:
        response = requests.get(f"{API_URL}/api/zonas")
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Zonas disponibles:")
        for zona in data['zonas']:
            print(f"  - {zona['nombre']} ({zona['id']})")
        
        assert response.status_code == 200
        assert len(data['zonas']) > 0, "No hay zonas disponibles"
        
        print("✅ PASÓ - Zonas recuperadas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ FALLÓ - {str(e)}")
        return False

def test_analizar_hogar():
    """Test 3: Análisis para hogar"""
    print_section("TEST 3: Análisis - Hogar en Monterrey (30 días)")
    
    try:
        payload = {
            "tipo_usuario": "hogar",
            "zona": "monterrey",
            "dias": 30
        }
        
        print(f"Enviando: {json.dumps(payload, indent=2)}")
        print("\n⏳ Consultando API Climate y generando sugerencia con IA...")
        
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/api/analizar",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start_time
        
        data = response.json()
        
        print(f"\n⏱️ Tiempo de respuesta: {elapsed:.2f} segundos")
        print(f"Status Code: {response.status_code}")
        
        if data.get('exito'):
            print("\n📊 MÉTRICAS CLIMÁTICAS:")
            metricas = data['metricas']
            print(f"  - Temperatura Promedio: {metricas['temp_promedio']}°C")
            print(f"  - Temperatura Máxima: {metricas['temp_maxima']}°C")
            print(f"  - Días con Calor Extremo: {metricas['dias_calor_extremo']}")
            print(f"  - Potencial Solar: {metricas['potencial_solar_promedio']} MJ/m²")
            print(f"  - Días Óptimos para Solar: {metricas['dias_optimos_solar']}")
            
            print("\n💡 SUGERENCIA GENERADA:")
            print("-" * 60)
            print(data['sugerencia'][:500])  # Primeros 500 caracteres
            if len(data['sugerencia']) > 500:
                print("... (sugerencia completa truncada)")
            print("-" * 60)
            
            print("\n📈 GRÁFICAS:")
            print(f"  - Temperatura: {'✓ Generada' if data['graficas']['temperatura'] else '✗ Error'}")
            print(f"  - Solar: {'✓ Generada' if data['graficas']['solar'] else '✗ Error'}")
            
            assert response.status_code == 200
            assert data['metricas']['temp_promedio'] > 0
            
            print("\n✅ PASÓ - Análisis completado exitosamente")
            return True
        else:
            print(f"❌ FALLÓ - {data.get('error', 'Error desconocido')}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FALLÓ - Timeout (la API tardó más de 60 segundos)")
        return False
    except Exception as e:
        print(f"❌ FALLÓ - {str(e)}")
        return False

def test_analizar_industria():
    """Test 4: Análisis para industria"""
    print_section("TEST 4: Análisis - Industria en CDMX (60 días)")
    
    try:
        payload = {
            "tipo_usuario": "industria",
            "zona": "cdmx",
            "dias": 60
        }
        
        print(f"Enviando: {json.dumps(payload, indent=2)}")
        print("\n⏳ Generando sugerencia industrial...")
        
        response = requests.post(
            f"{API_URL}/api/analizar",
            json=payload,
            timeout=60
        )
        
        data = response.json()
        
        if data.get('exito'):
            print("\n💡 SUGERENCIA INDUSTRIAL (primeras líneas):")
            print("-" * 60)
            print("\n".join(data['sugerencia'].split('\n')[:10]))
            print("-" * 60)
            
            print("\n✅ PASÓ - Sugerencia industrial generada")
            return True
        else:
            print(f"❌ FALLÓ - {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ FALLÓ - {str(e)}")
        return False

def test_validaciones():
    """Test 5: Validaciones de parámetros"""
    print_section("TEST 5: Validaciones de Entrada")
    
    tests = [
        {
            "nombre": "Tipo de usuario inválido",
            "payload": {"tipo_usuario": "invalido", "zona": "monterrey", "dias": 30},
            "debe_fallar": True
        },
        {
            "nombre": "Zona inexistente",
            "payload": {"tipo_usuario": "hogar", "zona": "marte", "dias": 30},
            "debe_fallar": True
        },
        {
            "nombre": "Días fuera de rango (muy pocos)",
            "payload": {"tipo_usuario": "hogar", "zona": "monterrey", "dias": 3},
            "debe_fallar": True
        },
        {
            "nombre": "Días fuera de rango (demasiados)",
            "payload": {"tipo_usuario": "hogar", "zona": "monterrey", "dias": 500},
            "debe_fallar": True
        }
    ]
    
    passed = 0
    
    for test in tests:
        print(f"\n  Testing: {test['nombre']}")
        
        try:
            response = requests.post(
                f"{API_URL}/api/analizar",
                json=test['payload'],
                timeout=10
            )
            
            if test['debe_fallar']:
                if response.status_code == 400:
                    print(f"    ✓ Rechazado correctamente (400)")
                    passed += 1
                else:
                    print(f"    ✗ Debió ser rechazado pero pasó")
            else:
                if response.status_code == 200:
                    print(f"    ✓ Aceptado correctamente")
                    passed += 1
                else:
                    print(f"    ✗ Debió pasar pero fue rechazado")
                    
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
    
    print(f"\nResultado: {passed}/{len(tests)} pruebas pasadas")
    
    if passed == len(tests):
        print("✅ PASÓ - Todas las validaciones funcionan")
        return True
    else:
        print("❌ FALLÓ - Algunas validaciones no funcionan")
        return False

def test_exportar_csv():
    """Test 6: Exportar CSV"""
    print_section("TEST 6: Exportar CSV")
    
    try:
        payload = {
            "zona": "guadalajara",
            "dias": 15
        }
        
        print(f"Solicitando CSV: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{API_URL}/api/exportar-csv",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            # Verificar que es un CSV válido
            content = response.content.decode('utf-8')
            lines = content.split('\n')
            
            print(f"\n📄 CSV Generado:")
            print(f"  - Líneas totales: {len(lines)}")
            print(f"  - Encabezados: {lines[0]}")
            print(f"  - Primera fila de datos: {lines[1] if len(lines) > 1 else 'N/A'}")
            
            # Verificar columnas esperadas
            headers = lines[0].split(',')
            expected_columns = ['Fecha', 'Temp_Promedio', 'Temp_Maxima']
            
            has_columns = all(col in headers for col in expected_columns)
            
            if has_columns:
                print("\n✅ PASÓ - CSV exportado correctamente")
                return True
            else:
                print("\n❌ FALLÓ - Faltan columnas esperadas")
                return False
        else:
            print(f"❌ FALLÓ - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FALLÓ - {str(e)}")
        return False

def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n")
    print("🧪" * 30)
    print("  ENERGY ADVISOR - SUITE DE TESTS")
    print("🧪" * 30)
    
    tests = [
        ("Health Check", test_health),
        ("Obtener Zonas", test_zonas),
        ("Análisis Hogar", test_analizar_hogar),
        ("Análisis Industria", test_analizar_industria),
        ("Validaciones", test_validaciones),
        ("Exportar CSV", test_exportar_csv)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(1)  # Pequeña pausa entre tests
        except Exception as e:
            print(f"\n❌ Error inesperado en {name}: {str(e)}")
            results.append((name, False))
    
    # Resumen final
    print_section("RESUMEN DE RESULTADOS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"  TOTAL: {passed}/{total} tests pasados ({(passed/total)*100:.1f}%)")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 ¡TODOS LOS TESTS PASARON! El backend está funcionando correctamente.\n")
        return True
    else:
        print("⚠️  Algunos tests fallaron. Revisa los errores arriba.\n")
        return False

if __name__ == "__main__":
    print("\n⚙️  Iniciando suite de tests...")
    print("📍 Backend URL:", API_URL)
    print("⏳ Esto puede tomar 1-2 minutos...\n")
    
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrumpidos por el usuario\n")
        exit(1)
