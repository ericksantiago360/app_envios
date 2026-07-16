// API Configuration
const API_BASE_URL = '/api';

// ---- Safari-safe localStorage wrapper ----
const store = {
    get(key) {
        try { return localStorage.getItem(key); } catch(e) { return null; }
    },
    set(key, value) {
        try { localStorage.setItem(key, value); } catch(e) { console.warn('localStorage no disponible'); }
    },
    remove(key) {
        try { localStorage.removeItem(key); } catch(e) {}
    }
};

// Limpiar payload: convierte strings vacíos a null
function cleanPayload(data) {
    const cleaned = {};
    for (const [key, value] of Object.entries(data)) {
        cleaned[key] = (value === '' || value === undefined) ? null : value;
    }
    return cleaned;
}

// API Helper Functions
const api = {
    async request(endpoint, options = {}) {
        const token = store.get('token');

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': 'Bearer ' + token }),
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(API_BASE_URL + endpoint, config);

            if (response.status === 401) {
                store.remove('token');
                store.remove('user');
                window.location.reload();
                throw new Error('Sesión expirada');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    Array.isArray(data.detail)
                        ? data.detail.map(function(e) { return e.msg; }).join(', ')
                        : data.detail || 'Error en la solicitud'
                );
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    auth: {
        async login(username, password) {
            return await api.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username: username, password: password })
            });
        },
        async register(userData) {
            return await api.request('/auth/register', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
        },
        async getCurrentUser() {
            return await api.request('/auth/me');
        }
    },

    envios: {
        async getAll(filters) {
            const params = new URLSearchParams(filters || {});
            return await api.request('/envios/?' + params);
        },
        async getById(id) {
            return await api.request('/envios/' + id);
        },
        async track(numeroGuia) {
            return await api.request('/envios/tracking/' + numeroGuia);
        },
        async create(envioData) {
            return await api.request('/envios/', { method: 'POST', body: JSON.stringify(envioData) });
        },
        async update(id, envioData) {
            return await api.request('/envios/' + id, { method: 'PUT', body: JSON.stringify(envioData) });
        },
        async delete(id) {
            return await api.request('/envios/' + id, { method: 'DELETE' });
        }
    },

    clientes: {
        async getAll(skip, limit) {
            return await api.request('/clientes/?skip=' + (skip || 0) + '&limit=' + (limit || 100));
        },
        async getById(id) {
            return await api.request('/clientes/' + id);
        },
        async create(clienteData) {
            return await api.request('/clientes/', { method: 'POST', body: JSON.stringify(clienteData) });
        },
        async update(id, clienteData) {
            return await api.request('/clientes/' + id, { method: 'PUT', body: JSON.stringify(clienteData) });
        },
        async delete(id) {
            return await api.request('/clientes/' + id, { method: 'DELETE' });
        }
    },

    repartidores: {
        async getAll(disponible) {
            const params = (disponible !== null && disponible !== undefined) ? '?disponible=' + disponible : '';
            return await api.request('/repartidores/' + params);
        },
        async getById(id) {
            return await api.request('/repartidores/' + id);
        },
        async create(data) {
            return await api.request('/repartidores/', { method: 'POST', body: JSON.stringify(data) });
        },
        async update(id, data) {
            return await api.request('/repartidores/' + id, { method: 'PUT', body: JSON.stringify(data) });
        },
        async delete(id) {
            return await api.request('/repartidores/' + id, { method: 'DELETE' });
        }
    },

    rutas: {
        async getAll(repartidorId, activa) {
            const params = new URLSearchParams();
            if (repartidorId) params.append('repartidor_id', repartidorId);
            if (activa !== null && activa !== undefined) params.append('activa', activa);
            return await api.request('/rutas/?' + params);
        },
        async getById(id) {
            return await api.request('/rutas/' + id);
        },
        async create(data) {
            return await api.request('/rutas/', { method: 'POST', body: JSON.stringify(data) });
        },
        async update(id, data) {
            return await api.request('/rutas/' + id, { method: 'PUT', body: JSON.stringify(data) });
        },
        async delete(id) {
            return await api.request('/rutas/' + id, { method: 'DELETE' });
        }
    }
};
