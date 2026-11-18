# 🚀 Guía de Inicio Rápido

## Iniciar el Sistema en 3 Pasos

### 1️⃣ Configurar variables de entorno y levantar los contenedores
```bash
cd envios-app
cp .env.example .env
# Edita .env: pon una SECRET_KEY propia y cambia las contraseñas de MySQL
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
docker-compose up -d
```

### 2️⃣ Esperar a que MySQL inicie (30 segundos aprox)
```bash
# Ver logs para verificar
docker-compose logs -f db
# Presiona Ctrl+C cuando veas "ready for connections"
```

### 3️⃣ Abrir el navegador
```
http://localhost
```

## 🎯 Credenciales Iniciales

Puedes crear tu primer usuario desde la interfaz o usar el script de datos de prueba:

### Opción A: Crear desde la Web
1. Ir a http://localhost
2. Clic en "Regístrate aquí"
3. Llenar formulario y seleccionar rol
4. Registrarse

### Opción B: Cargar Datos de Prueba
```bash
# Ejecutar script de inicialización
docker-compose exec backend python init_data.py
```

Esto creará usuarios de prueba:
- **Admin**: usuario `admin` / password `admin123`
- **Repartidor**: usuario `carlos_rep` / password `rep123`
- **Cliente**: usuario `juan_cliente` / password `cliente123`

## 📊 URLs Importantes

- **Aplicación**: http://localhost
- **API Docs**: http://localhost/docs
- **API Backend**: http://localhost:8000

## 🛠️ Comandos Útiles

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs
docker-compose logs -f

# Detener todo
docker-compose down

# Reiniciar
docker-compose restart

# Limpiar todo (incluyendo base de datos)
docker-compose down -v
```

## 🎮 Flujo de Trabajo Básico

1. **Iniciar sesión** como admin
2. **Crear clientes** desde el menú Clientes
3. **Crear repartidores** desde el menú Repartidores
4. **Crear rutas** y asignarlas a repartidores
5. **Crear envíos** asignando origen, destino y repartidor
6. **Actualizar estados** de los envíos según avancen

## 🆘 Solución de Problemas

### Error de conexión a MySQL
```bash
# Esperar más tiempo y verificar que MySQL esté listo
docker-compose logs db | grep "ready for connections"
```

### Puerto 80 ya está en uso
```bash
# Cambiar puerto en docker-compose.yml
# En la sección frontend, cambiar "80:80" a "8080:80"
# Luego acceder en http://localhost:8080
```

### Cambios no se reflejan
```bash
# Reconstruir imágenes
docker-compose up -d --build
```

## 💡 Tips

- Los envíos generan automáticamente un número de guía único
- Los clientes pueden ver solo sus envíos
- Los repartidores solo ven envíos asignados a ellos
- Los admins tienen acceso completo a todo
- El sistema usa JWT para autenticación (tokens expiran en 30 min)

¡Listo para usar! 🎉
