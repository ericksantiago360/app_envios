// Envios Manager
const enviosManager = {
    clientes: [],
    repartidores: [],

    async init() {
        // Load clientes and repartidores for dropdowns
        try {
            this.clientes = await api.clientes.getAll();
            this.repartidores = await api.repartidores.getAll();
        } catch (error) {
            console.error('Error loading data:', error);
        }

        // Setup event listeners
        const btnNuevoEnvio = document.getElementById('btnNuevoEnvio');
        if (btnNuevoEnvio) {
            btnNuevoEnvio.addEventListener('click', () => this.showCreateModal());
        }

        const filterEstado = document.getElementById('filterEstado');
        if (filterEstado) {
            filterEstado.addEventListener('change', () => this.load());
        }
    },

    async load() {
        try {
            const filterEstado = document.getElementById('filterEstado').value;
            const filters = filterEstado ? { estado: filterEstado } : {};
            
            const envios = await api.envios.getAll(filters);
            this.render(envios);
        } catch (error) {
            showToast('Error al cargar envíos: ' + error.message, 'error');
        }
    },

    render(envios) {
        const container = document.getElementById('enviosList');
        
        if (envios.length === 0) {
            container.innerHTML = '<p class="text-center">No hay envíos para mostrar</p>';
            return;
        }

        const rows = envios.map(envio => [
            envio.numero_guia,
            envio.descripcion || '-',
            envio.ciudad_origen,
            envio.ciudad_destino,
            getEstadoBadge(envio.estado),
            formatDate(envio.fecha_creacion),
            formatCurrency(envio.costo),
            `
                <div class="action-buttons">
                    <button class="btn-icon" onclick="enviosManager.showEditModal(${envio.id})" title="Editar">✏️</button>
                    <button class="btn-icon" onclick="enviosManager.showDetails(${envio.id})" title="Ver">👁️</button>
                    ${auth.getCurrentUser().role === 'admin' ? 
                        `<button class="btn-icon" onclick="enviosManager.delete(${envio.id})" title="Eliminar">🗑️</button>` : 
                        ''}
                </div>
            `
        ]);

        container.innerHTML = createTable(
            ['Guía', 'Descripción', 'Origen', 'Destino', 'Estado', 'Fecha', 'Costo', 'Acciones'],
            rows
        );
    },

    showCreateModal() {
        const clientesOptions = this.clientes.map(c => 
            `<option value="${c.id}">${c.nombre} ${c.apellido}</option>`
        ).join('');

        const repartidoresOptions = this.repartidores.map(r => 
            `<option value="${r.id}">${r.nombre} ${r.apellido}</option>`
        ).join('');

        const content = `
            <form id="envioForm">
                <div class="form-group">
                    <label>Cliente Origen</label>
                    <select name="cliente_origen_id" required>
                        <option value="">Seleccionar...</option>
                        ${clientesOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label>Cliente Destino</label>
                    <select name="cliente_destino_id" required>
                        <option value="">Seleccionar...</option>
                        ${clientesOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label>Repartidor (opcional)</label>
                    <select name="repartidor_id">
                        <option value="">Sin asignar</option>
                        ${repartidoresOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label>Descripción</label>
                    <textarea name="descripcion" rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label>Peso (kg)</label>
                    <input type="number" name="peso" step="0.01">
                </div>
                <div class="form-group">
                    <label>Dirección Origen</label>
                    <input type="text" name="direccion_origen" required>
                </div>
                <div class="form-group">
                    <label>Ciudad Origen</label>
                    <input type="text" name="ciudad_origen" required>
                </div>
                <div class="form-group">
                    <label>Dirección Destino</label>
                    <input type="text" name="direccion_destino" required>
                </div>
                <div class="form-group">
                    <label>Ciudad Destino</label>
                    <input type="text" name="ciudad_destino" required>
                </div>
                <div class="form-group">
                    <label>Costo</label>
                    <input type="number" name="costo" step="0.01" required>
                </div>
                <button type="submit" class="btn-primary">Crear Envío</button>
            </form>
        `;

        createModal('Nuevo Envío', content);

        document.getElementById('envioForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            let data = cleanPayload(Object.fromEntries(formData));

            // Convertir a tipos correctos
            data.cliente_origen_id = parseInt(data.cliente_origen_id);
            data.cliente_destino_id = parseInt(data.cliente_destino_id);
            data.repartidor_id = data.repartidor_id ? parseInt(data.repartidor_id) : null;
            data.peso  = data.peso  ? parseFloat(data.peso)  : null;
            data.alto  = data.alto  ? parseFloat(data.alto)  : null;
            data.ancho = data.ancho ? parseFloat(data.ancho) : null;
            data.largo = data.largo ? parseFloat(data.largo) : null;
            data.costo = data.costo ? parseFloat(data.costo) : 0;

            try {
                await api.envios.create(data);
                showToast('Envío creado exitosamente', 'success');
                closeModal();
                this.load();
            } catch (error) {
                showToast('Error al crear envío: ' + error.message, 'error');
            }
        });
    },

    async showDetails(id) {
        try {
            const envio = await api.envios.getById(id);
            
            const content = `
                <div class="details">
                    <p><strong>Número de Guía:</strong> ${envio.numero_guia}</p>
                    <p><strong>Estado:</strong> ${getEstadoBadge(envio.estado)}</p>
                    <p><strong>Descripción:</strong> ${envio.descripcion || '-'}</p>
                    <p><strong>Peso:</strong> ${envio.peso ? envio.peso + ' kg' : '-'}</p>
                    <hr>
                    <p><strong>Origen:</strong> ${envio.direccion_origen}, ${envio.ciudad_origen}</p>
                    <p><strong>Destino:</strong> ${envio.direccion_destino}, ${envio.ciudad_destino}</p>
                    <hr>
                    <p><strong>Costo:</strong> ${formatCurrency(envio.costo)}</p>
                    <p><strong>Fecha Creación:</strong> ${formatDate(envio.fecha_creacion)}</p>
                    <p><strong>Fecha Entrega Estimada:</strong> ${formatDate(envio.fecha_entrega_estimada)}</p>
                </div>
            `;
            
            createModal('Detalles del Envío', content);
        } catch (error) {
            showToast('Error al cargar detalles: ' + error.message, 'error');
        }
    },

    async showEditModal(id) {
        try {
            const envio = await api.envios.getById(id);
            const currentUser = auth.getCurrentUser();

            const content = `
                <form id="editEnvioForm">
                    <div class="form-group">
                        <label>Estado</label>
                        <select name="estado" required ${currentUser.role === 'cliente' ? 'disabled' : ''}>
                            <option value="pendiente" ${envio.estado === 'pendiente' ? 'selected' : ''}>Pendiente</option>
                            <option value="en_transito" ${envio.estado === 'en_transito' ? 'selected' : ''}>En Tránsito</option>
                            <option value="entregado" ${envio.estado === 'entregado' ? 'selected' : ''}>Entregado</option>
                            <option value="cancelado" ${envio.estado === 'cancelado' ? 'selected' : ''}>Cancelado</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Notas</label>
                        <textarea name="notas" rows="3">${envio.notas || ''}</textarea>
                    </div>
                    <button type="submit" class="btn-primary">Actualizar</button>
                </form>
            `;

            createModal('Actualizar Envío', content);

            document.getElementById('editEnvioForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);

                try {
                    await api.envios.update(id, data);
                    showToast('Envío actualizado exitosamente', 'success');
                    closeModal();
                    this.load();
                } catch (error) {
                    showToast('Error al actualizar: ' + error.message, 'error');
                }
            });
        } catch (error) {
            showToast('Error al cargar envío: ' + error.message, 'error');
        }
    },

    async delete(id) {
        if (!confirm('¿Estás seguro de eliminar este envío?')) return;

        try {
            await api.envios.delete(id);
            showToast('Envío eliminado exitosamente', 'success');
            this.load();
        } catch (error) {
            showToast('Error al eliminar: ' + error.message, 'error');
        }
    }
};
