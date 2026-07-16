// Mapa Manager con Google Maps
let googleMapsReady = false;
let map = null;
let markers = [];
let infoWindows = [];
let gpsWatchId = null;

// Callback cuando Google Maps está listo
window.initGoogleMaps = function() {
    googleMapsReady = true;
    console.log('Google Maps API cargado');
};

const mapaManager = {
    async init() {
        const btnCentrar = document.getElementById('btnCentrarMapa');
        const btnActualizar = document.getElementById('btnActualizarMapa');
        const filterEstado = document.getElementById('mapFilterEstado');

        if (btnCentrar) {
            btnCentrar.addEventListener('click', () => this.centrarMapa());
        }

        if (btnActualizar) {
            btnActualizar.addEventListener('click', () => this.load());
        }

        if (filterEstado) {
            filterEstado.addEventListener('click', () => this.load());
        }

        // Si el usuario es repartidor, iniciar tracking GPS
        const currentUser = auth.getCurrentUser();
        if (currentUser && currentUser.role === 'repartidor') {
            this.iniciarTrackingGPS();
        }
    },

    async load() {
        // Esperar a que Google Maps esté listo
        if (!googleMapsReady) {
            showToast('Cargando Google Maps...', 'info');
            setTimeout(() => this.load(), 1000);
            return;
        }

        // Inicializar mapa si no existe
        if (!map) {
            this.initMap();
        }

        try {
            await this.cargarDatos();
        } catch (error) {
            showToast('Error al cargar datos del mapa: ' + error.message, 'error');
        }
    },

    initMap() {
        const mapElement = document.getElementById('map');
        if (!mapElement) return;

        // Centro en Ciudad de México por defecto
        const center = { lat: 19.4326, lng: -99.1332 };

        map = new google.maps.Map(mapElement, {
            zoom: 12,
            center: center,
            mapTypeControl: true,
            streetViewControl: false,
            fullscreenControl: true,
            zoomControl: true,
            styles: [
                {
                    featureType: 'poi',
                    elementType: 'labels',
                    stylers: [{ visibility: 'off' }]
                }
            ]
        });

        console.log('Mapa inicializado');
    },

    async cargarDatos() {
        this.limpiarMarcadores();

        const filterEstado = document.getElementById('mapFilterEstado').value;

        // Cargar repartidores
        try {
            const response = await fetch('/api/tracking/repartidores', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const repartidores = await response.json();
            this.dibujarRepartidores(repartidores);
        } catch (error) {
            console.error('Error cargando repartidores:', error);
        }

        // Cargar envíos
        try {
            const url = filterEstado 
                ? `/api/tracking/envios?estado=${filterEstado}`
                : '/api/tracking/envios';

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            const envios = await response.json();
            this.dibujarEnvios(envios);
        } catch (error) {
            console.error('Error cargando envíos:', error);
        }
    },

    dibujarRepartidores(repartidores) {
        repartidores.forEach(rep => {
            if (!rep.lat_actual || !rep.lng_actual) return;

            const position = {
                lat: rep.lat_actual,
                lng: rep.lng_actual
            };

            // Icono personalizado según disponibilidad
            const icon = {
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: rep.disponible ? '#10b981' : '#ef4444',
                fillOpacity: 1,
                strokeColor: '#ffffff',
                strokeWeight: 2,
                scale: 10
            };

            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: `${rep.nombre} ${rep.apellido}`,
                icon: icon,
                label: {
                    text: '🚚',
                    fontSize: '16px'
                }
            });

            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div style="padding: 10px;">
                        <h4>${rep.nombre} ${rep.apellido}</h4>
                        <p><strong>Vehículo:</strong> ${rep.vehiculo || 'N/A'}</p>
                        <p><strong>Estado:</strong> ${rep.disponible ? '✅ Disponible' : '⛔ No Disponible'}</p>
                        <p><small>Última actualización: ${this.formatearFecha(rep.ultima_actualizacion_gps)}</small></p>
                    </div>
                `
            });

            marker.addListener('click', () => {
                this.cerrarInfoWindows();
                infoWindow.open(map, marker);
            });

            markers.push(marker);
            infoWindows.push(infoWindow);
        });
    },

    dibujarEnvios(envios) {
        envios.forEach(envio => {
            // Marcador de origen
            if (envio.lat_origen && envio.lng_origen) {
                const markerOrigen = new google.maps.Marker({
                    position: { lat: envio.lat_origen, lng: envio.lng_origen },
                    map: map,
                    title: `Origen: ${envio.numero_guia}`,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        fillColor: '#f59e0b',
                        fillOpacity: 1,
                        strokeColor: '#ffffff',
                        strokeWeight: 2,
                        scale: 8
                    },
                    label: {
                        text: '📦',
                        fontSize: '14px'
                    }
                });

                const infoOrigen = new google.maps.InfoWindow({
                    content: `
                        <div style="padding: 10px;">
                            <h4>Origen: ${envio.numero_guia}</h4>
                            <p>${envio.direccion_origen}</p>
                            <p>${envio.ciudad_origen}</p>
                            <p><strong>Estado:</strong> ${this.getEstadoText(envio.estado)}</p>
                        </div>
                    `
                });

                markerOrigen.addListener('click', () => {
                    this.cerrarInfoWindows();
                    infoOrigen.open(map, markerOrigen);
                });

                markers.push(markerOrigen);
                infoWindows.push(infoOrigen);
            }

            // Marcador de destino
            if (envio.lat_destino && envio.lng_destino) {
                const markerDestino = new google.maps.Marker({
                    position: { lat: envio.lat_destino, lng: envio.lng_destino },
                    map: map,
                    title: `Destino: ${envio.numero_guia}`,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        fillColor: '#2563eb',
                        fillOpacity: 1,
                        strokeColor: '#ffffff',
                        strokeWeight: 2,
                        scale: 8
                    },
                    label: {
                        text: '🎯',
                        fontSize: '14px'
                    }
                });

                const infoDestino = new google.maps.InfoWindow({
                    content: `
                        <div style="padding: 10px;">
                            <h4>Destino: ${envio.numero_guia}</h4>
                            <p>${envio.direccion_destino}</p>
                            <p>${envio.ciudad_destino}</p>
                            <p><strong>Estado:</strong> ${this.getEstadoText(envio.estado)}</p>
                        </div>
                    `
                });

                markerDestino.addListener('click', () => {
                    this.cerrarInfoWindows();
                    infoDestino.open(map, markerDestino);
                });

                markers.push(markerDestino);
                infoWindows.push(infoDestino);

                // Dibujar línea entre origen y destino
                if (envio.lat_origen && envio.lng_origen) {
                    const linea = new google.maps.Polyline({
                        path: [
                            { lat: envio.lat_origen, lng: envio.lng_origen },
                            { lat: envio.lat_destino, lng: envio.lng_destino }
                        ],
                        geodesic: true,
                        strokeColor: envio.estado === 'entregado' ? '#10b981' : '#2563eb',
                        strokeOpacity: 0.5,
                        strokeWeight: 2,
                        map: map
                    });

                    markers.push(linea); // Para limpiarlo después
                }
            }
        });
    },

    limpiarMarcadores() {
        markers.forEach(marker => {
            if (marker.setMap) {
                marker.setMap(null);
            }
        });
        markers = [];
        this.cerrarInfoWindows();
        infoWindows = [];
    },

    cerrarInfoWindows() {
        infoWindows.forEach(iw => iw.close());
    },

    centrarMapa() {
        if (!map || markers.length === 0) return;

        const bounds = new google.maps.LatLngBounds();
        markers.forEach(marker => {
            if (marker.getPosition) {
                bounds.extend(marker.getPosition());
            }
        });
        map.fitBounds(bounds);
    },

    getEstadoText(estado) {
        const estados = {
            'pendiente': '⏳ Pendiente',
            'en_transito': '🚚 En Tránsito',
            'entregado': '✅ Entregado',
            'cancelado': '❌ Cancelado'
        };
        return estados[estado] || estado;
    },

    formatearFecha(fecha) {
        if (!fecha) return 'N/A';
        return new Date(fecha).toLocaleString('es-MX');
    },

    // Tracking GPS para repartidores
    iniciarTrackingGPS() {
        if (!navigator.geolocation) {
            console.log('Geolocalización no soportada');
            return;
        }

        showToast('Tracking GPS activado', 'success');

        gpsWatchId = navigator.geolocation.watchPosition(
            (position) => {
                this.actualizarUbicacionRepartidor(
                    position.coords.latitude,
                    position.coords.longitude
                );
            },
            (error) => {
                console.error('Error GPS:', error);
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    },

    async actualizarUbicacionRepartidor(lat, lng) {
        try {
            await fetch('/api/tracking/repartidor/ubicacion', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ lat, lng })
            });
            console.log('Ubicación GPS actualizada:', lat, lng);
        } catch (error) {
            console.error('Error actualizando GPS:', error);
        }
    },

    detenerTrackingGPS() {
        if (gpsWatchId) {
            navigator.geolocation.clearWatch(gpsWatchId);
            gpsWatchId = null;
            console.log('Tracking GPS detenido');
        }
    }
};
