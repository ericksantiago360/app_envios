# 📦 Sistema de Gestión de Envíos

Sistema completo de gestión de envíos y entregas con autenticación multi-rol, desarrollado con FastAPI, MySQL, Docker Compose y frontend vanilla JavaScript.

## 🚀 Características

### Funcionalidades Principales
- ✅ **Gestión completa de envíos** - Crear, editar, rastrear y gestionar envíos
- 👥 **Gestión de clientes** - Registro y administración de clientes
- 🚚 **Gestión de repartidores** - Control de repartidores y su disponibilidad
- 🗺️ **Gestión de rutas** - Asignación de rutas y zonas de entrega
- 🔐 **Autenticación JWT** - Sistema seguro de autenticación
- 👔 **Roles múltiples** - Admin, Repartidor, Cliente
- 📊 **Dashboard** - Estadísticas y vista general del sistema
- 🔍 **Tracking** - Seguimiento de envíos por número de guía

### Roles de Usuario

#### 👑 Administrador
- Acceso completo al sistema
- Crear/editar/eliminar clientes, repartidores, rutas y envíos
- Ver todas las estadísticas

#### 🚚 Repartidor
- Ver envíos asignados
- Actualizar estado de envíos
- Gestionar su disponibilidad

#### 📦 Cliente
- Ver sus envíos (como origen o destino)
- Rastrear envíos
- Ver historial

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Python 3.11**
- **SQLAlchemy** - ORM para base de datos
- **MySQL 8.0** - Base de datos relacional
- **PyMySQL** - Driver de MySQL
- **JWT** - Autenticación con tokens
- **Uvicorn** - Servidor ASGI

### Frontend
- **HTML5**
- **CSS3** (Variables CSS, Grid, Flexbox)
- **JavaScript Vanilla** - Sin frameworks
- **Fetch API** - Comunicación con backend

### DevOps
- **Docker** - Contenedorización
- **Docker Compose** - Orquestación de servicios
- **Nginx** - Servidor web y proxy reverso

## 📁 Estructura del Proyecto

```
envios-app/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuración y seguridad
│   │   ├── db/             # Configuración de base de datos
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── routers/        # Endpoints de API
│   │   ├── schemas/        # Schemas Pydantic
│   │   └── main.py         # Aplicación FastAPI
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── styles.css      # Estilos de la app (dashboard)
│   │   │   └── landing.css     # Estilos de la landing page
│   │   └── js/
│   │       ├── api.js
│   │       ├── auth.js
│   │       ├── ui.js
│   │       ├── mapa.js
│   │       ├── envios.js
│   │       ├── clientes.js
│   │       ├── repartidores.js
│   │       ├── rutas.js
│   │       ├── app.js
│   │       └── landing.js      # Lógica de la landing page
│   ├── index.html              # 🏠 Landing page pública (estilo Lalamove)
│   └── app.html                # 🔐 Aplicación / Dashboard (requiere login)
├── docker-compose.yml
├── nginx.conf
└── README.md
```

### 🏠 Landing Page Pública

`index.html` es la página de inicio pública del sitio, inspirada en el modelo de **envios**. Incluye:

- **Hero** con CTA principal y widget de **rastreo de envíos en vivo** (conectado a `/api/envios/tracking/{numero_guia}`, sin necesidad de iniciar sesión)
- Tarjetas de servicio: **Para empresa / Para mí / Quiero ser repartidor**
- Sección de ventajas (rápido, económico, 24/7, rastreo en tiempo real)
- Tabs interactivos de **tipos de vehículo y tarifas** (moto, auto, SUV, pickup, camioneta, van, camión)
- CTA final y footer con enlaces de contacto

Desde la landing, los botones "Regístrate ahora" e "Iniciar sesión" llevan a `app.html`, que es la aplicación real (dashboard, envíos, mapa GPS, etc.). El botón "Quiero ser repartidor" preselecciona automáticamente el rol `repartidor` en el formulario de registro.

## 🚀 Instalación y Uso

### Prerequisitos
- Docker
- Docker Compose
- Git

### 1. Clonar el Repositorio
```bash
git clone <tu-repositorio>
cd envios-app
```

### 2. Configurar Variables de Entorno (Opcional)
```bash
cp .env.example .env
# Editar .env si necesitas cambiar las credenciales
```

### 3. Iniciar los Servicios
```bash
docker-compose up -d
```

Esto iniciará tres servicios:
- **MySQL** en puerto 3306
- **Backend FastAPI** en puerto 8000
- **Frontend Nginx** en puerto 80

### 4. Verificar que todo está funcionando
```bash
# Ver logs
docker-compose logs -f

# Verificar contenedores
docker-compose ps
```

### 5. Acceder a la Aplicación

- **Frontend**: http://localhost
- **API Docs**: http://localhost/docs
- **API Backend**: http://localhost:8000

## 👤 Crear Primer Usuario

### Opción 1: Desde la interfaz web
1. Ir a http://localhost
2. Hacer clic en "Regístrate aquí"
3. Llenar el formulario con tu información
4. Seleccionar el rol deseado
5. Hacer clic en "Registrarse"

### Opción 2: Usando la API directamente
```bash
curl -X POST "http://localhost/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@ejemplo.com",
    "full_name": "Administrador",
    "role": "admin",
    "password": "admin123"
  }'
```

## 📚 Uso del Sistema

### Dashboard
- Vista general con estadísticas de envíos
- Total de envíos, en tránsito, entregados y pendientes
- Lista de envíos recientes

### Gestión de Envíos
1. Ir a "Envíos" en el menú
2. Hacer clic en "+ Nuevo Envío"
3. Llenar el formulario con:
   - Cliente origen y destino
   - Direcciones
   - Detalles del paquete
   - Costo
4. Guardar el envío

### Tracking de Envíos
- Cada envío genera un número de guía único
- Formato: `ENV-YYYYMMDDHHMMSS-XXXXXX`
- Se puede rastrear desde la lista de envíos

### Gestión de Clientes
- Crear nuevos clientes con información completa
- Editar datos de contacto y dirección
- Asociar clientes con usuarios del sistema

### Gestión de Repartidores (Solo Admin)
- Registrar nuevos repartidores
- Asignar vehículos
- Controlar disponibilidad
- Ver envíos asignados

### Gestión de Rutas (Solo Admin)
- Crear rutas de entrega
- Asignar zonas y horarios
- Vincular con repartidores
- Activar/desactivar rutas

## 🔧 Comandos Útiles

### Detener los servicios
```bash
docker-compose down
```

### Ver logs en tiempo real
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Reiniciar un servicio específico
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Acceder a la base de datos
```bash
docker-compose exec db mysql -u envios_user -penvios_pass envios_db
```

### Limpiar todo (incluyendo volúmenes)
```bash
docker-compose down -v
```

## 🔐 Seguridad

### En Producción
1. **Cambiar SECRET_KEY** en variables de entorno
2. **Usar contraseñas seguras** para MySQL
3. **Configurar HTTPS** con certificados SSL
4. **Limitar CORS** en backend (actualmente permite todos los orígenes)
5. **Usar variables de entorno** para credenciales sensibles

## 🌐 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener usuario actual

### Envíos
- `GET /api/envios/` - Listar envíos
- `POST /api/envios/` - Crear envío
- `GET /api/envios/{id}` - Obtener envío
- `PUT /api/envios/{id}` - Actualizar envío
- `DELETE /api/envios/{id}` - Eliminar envío
- `GET /api/envios/tracking/{numero_guia}` - Rastrear envío

### Clientes
- `GET /api/clientes/` - Listar clientes
- `POST /api/clientes/` - Crear cliente
- `GET /api/clientes/{id}` - Obtener cliente
- `PUT /api/clientes/{id}` - Actualizar cliente
- `DELETE /api/clientes/{id}` - Eliminar cliente

### Repartidores
- `GET /api/repartidores/` - Listar repartidores
- `POST /api/repartidores/` - Crear repartidor
- `GET /api/repartidores/{id}` - Obtener repartidor
- `PUT /api/repartidores/{id}` - Actualizar repartidor
- `DELETE /api/repartidores/{id}` - Eliminar repartidor

### Rutas
- `GET /api/rutas/` - Listar rutas
- `POST /api/rutas/` - Crear ruta
- `GET /api/rutas/{id}` - Obtener ruta
- `PUT /api/rutas/{id}` - Actualizar ruta
- `DELETE /api/rutas/{id}` - Eliminar ruta

Documentación completa en: http://localhost/docs

## 🐛 Solución de Problemas

### El backend no inicia
```bash
# Ver logs
docker-compose logs backend

# Verificar que MySQL esté listo
docker-compose logs db
```

### Error de conexión a MySQL
- Esperar unos segundos más, MySQL puede tardar en inicializarse
- Verificar las credenciales en docker-compose.yml

### Cambios en código no se reflejan
```bash
# Reconstruir imágenes
docker-compose up -d --build
```

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si encuentras algún problema o tienes preguntas, por favor abre un issue en el repositorio.

---

Desarrollado con ❤️ usando FastAPI, MySQL y Docker
# app_envios
