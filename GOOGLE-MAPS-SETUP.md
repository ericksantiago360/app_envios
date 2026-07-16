# 🗺️ Configuración de Google Maps API

Para que el mapa funcione correctamente, necesitas obtener una API Key de Google Maps.

## Pasos para Obtener la API Key

### 1. Ir a Google Cloud Console
Visita: https://console.cloud.google.com/

### 2. Crear un Proyecto (si no tienes uno)
1. Haz clic en el selector de proyectos en la parte superior
2. Clic en "Nuevo Proyecto"
3. Nombra tu proyecto (ej: "EnviosApp")
4. Haz clic en "Crear"

### 3. Habilitar las APIs Necesarias
1. Ve a "APIs y servicios" > "Biblioteca"
2. Busca y habilita las siguientes APIs:
   - **Maps JavaScript API**
   - **Geocoding API** (para convertir direcciones en coordenadas)
   - **Directions API** (opcional, para rutas optimizadas)
   - **Geolocation API** (para tracking GPS)

### 4. Crear Credenciales (API Key)
1. Ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "+ CREAR CREDENCIALES"
3. Selecciona "Clave de API"
4. Copia la API Key generada

### 5. Configurar la API Key en el Proyecto

**Opción A: Para Desarrollo (Fácil)**
Edita `frontend/index.html` y reemplaza `TU_API_KEY`:

```html
<script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&callback=initGoogleMaps"></script>
```

**Opción B: Para Producción (Recomendado)**
1. Restringe la API Key por dominio en Google Cloud Console
2. Configúrala como variable de entorno en el servidor

### 6. Restricciones de Seguridad (IMPORTANTE)

En Google Cloud Console > Credenciales > Tu API Key:

**Restricciones de la aplicación:**
- **Para desarrollo local**: Selecciona "Referentes HTTP" y agrega:
  - `http://localhost`
  - `http://localhost:80`
  - `http://127.0.0.1`

- **Para producción**: Agrega tu dominio:
  - `https://tudominio.com/*`

**Restricciones de API:**
- Selecciona "Restringir clave"
- Marca solo las APIs que habilitaste

## Uso del Mapa sin API Key (Limitado)

Si no quieres configurar Google Maps ahora, puedes usar OpenStreetMap como alternativa temporal:

1. Instala Leaflet (librería open source)
2. Reemplaza el script de Google Maps por Leaflet
3. **Nota**: Perderás algunas funcionalidades avanzadas

## Costos de Google Maps

Google Maps ofrece **$200 USD de crédito gratuito mensual**, que cubre:
- ~28,000 cargas de mapa dinámico
- ~40,000 geocodificaciones

Para la mayoría de aplicaciones pequeñas/medianas, esto es suficiente y **no pagarás nada**.

## Geocodificación de Direcciones

El sistema necesita convertir direcciones a coordenadas GPS. Hay dos opciones:

### Opción 1: Geocodificar al Crear Envío (Automático)
Agrega este código al backend en `routers/envios.py`:

```python
import requests

def geocodificar_direccion(direccion, ciudad):
    """Convertir dirección a lat/lng usando Google Geocoding API"""
    api_key = "TU_API_KEY"
    url = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": f"{direccion}, {ciudad}",
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None
```

### Opción 2: Geocodificar Manualmente (Por Ahora)
Mientras configuras la API, puedes usar coordenadas de ejemplo:

**Ciudad de México**: `lat: 19.4326, lng: -99.1332`
**Guadalajara**: `lat: 20.6597, lng: -103.3496`
**Monterrey**: `lat: 25.6866, lng: -100.3161`

## Funcionalidades Implementadas

✅ **Mapa interactivo** con marcadores personalizados
✅ **Tracking GPS en tiempo real** para repartidores
✅ **Visualización de envíos** (origen y destino)
✅ **Actualización automática** de ubicación de repartidores
✅ **Filtros por estado** de envío
✅ **Info windows** con detalles al hacer clic
✅ **Leyenda** explicativa
✅ **Líneas conectando** origen y destino

## Próximos Pasos Sugeridos

1. **Rutas optimizadas**: Usar Directions API para calcular la mejor ruta
2. **Geocodificación automática**: Al crear un envío, geocodificar automáticamente
3. **Notificaciones push**: Avisar cuando el repartidor está cerca
4. **Historial de ruta**: Guardar el recorrido completo del repartidor
5. **Zonas de entrega**: Dibujar polígonos en el mapa para rutas

## Soporte

Si tienes problemas:
1. Verifica que las APIs estén habilitadas en Google Cloud
2. Revisa que la API Key no tenga restricciones que bloqueen localhost
3. Abre la consola del navegador para ver errores de JavaScript
4. Verifica que el navegador permita geolocalización (HTTPS requerido en producción)

---

¡Con esto tendrás un sistema completo de tracking GPS en tiempo real! 🚀📍
