// Rutas Manager
const rutasManager = {
    repartidores: [],

    async init() {
        // Load repartidores for dropdowns
        try {
            this.repartidores = await api.repartidores.getAll();
        } catch (error) {
            console.error('Error loading repartidores:', error);
        }

        const btnNuevaRuta = document.getElementById('btnNuevaRuta');
        if (btnNuevaRuta) {
            btnNuevaRuta.addEventListener('click', () => this.showCreateModal());
        }
    },

    async load() {
        try {
            const rutas = await api.rutas.getAll();
            this.render(rutas);
        } catch (error) {
            showToast('Error al cargar rutas: ' + error.message, 'error');
        }
    },

    render(rutas) {
        const container = document.getElementById('rutasList');
        
        if (rutas.length === 0) {
            container.innerHTML = '<p class="text-center">No hay rutas registradas</p>';
            return;
        }

        const rows = rutas.map(ruta => {
            const repartidor = this.repartidores.find(r => r.id === ruta.repartidor_id);
            const repartidorNombre = repartidor ? `${repartidor.nombre} ${repartidor.apellido}` : 'N/A';
            
            return [
                ruta.id,
                ruta.nombre,
                repartidorNombre,
                ruta.zonas || '-',
                ruta.dias_activos || '-',
                ruta.hora_inicio && ruta.hora_fin ? `${ruta.hora_inicio} - ${ruta.hora_fin}` : '-',
                ruta.activa ? 
                    '<span class="badge badge-success">Activa</span>' : 
                    '<span class="badge badge-danger">Inactiva</span>',
                `
                    <div class="action-buttons">
                        <button class="btn-icon" onclick="rutasManager.showEditModal(${ruta.id})" title="Editar">✏️</button>
                        <button class="btn-icon" onclick="rutasManager.toggleActiva(${ruta.id}, ${!ruta.activa})" title="Activar/Desactivar">
                            ${ruta.activa ? '⏸️' : '▶️'}
                        </button>
                        <button class="btn-icon" onclick="rutasManager.delete(${ruta.id})" title="Eliminar">🗑️</button>
                    </div>
                `
            ];
        });

        container.innerHTML = createTable(
            ['ID', 'Nombre', 'Repartidor', 'Zonas', 'Días', 'Horario', 'Estado', 'Acciones'],
            rows
        );
    },

    showCreateModal() {
        const repartidoresOptions = this.repartidores.map(r => 
            `<option value="${r.id}">${r.nombre} ${r.apellido}</option>`
        ).join('');

        const content = `
            <form id="rutaForm">
                <div class="form-group">
                    <label>Nombre de la Ruta</label>
                    <input type="text" name="nombre" required placeholder="Ej: Ruta Norte">
                </div>
                <div class="form-group">
                    <label>Repartidor Asignado</label>
                    <select name="repartidor_id" required>
                        <option value="">Seleccionar...</option>
                        ${repartidoresOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label>Descripción</label>
                    <textarea name="descripcion" rows="2"></textarea>
                </div>
                <div class="form-group">
                    <label>Zonas (separadas por coma)</label>
                    <input type="text" name="zonas" placeholder="Ej: Centro, Norte, Poniente">
                </div>
                <div class="form-group">
                    <label>Hora Inicio</label>
                    <input type="time" name="hora_inicio">
                </div>
                <div class="form-group">
                    <label>Hora Fin</label>
                    <input type="time" name="hora_fin">
                </div>
                <div class="form-group">
                    <label>Días Activos (separados por coma)</label>
                    <input type="text" name="dias_activos" placeholder="Ej: lun,mar,mie,jue,vie">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="activa" checked>
                        Activa
                    </label>
                </div>
                <button type="submit" class="btn-primary">Crear Ruta</button>
            </form>
        `;

        createModal('Nueva Ruta', content);

        document.getElementById('rutaForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            data.repartidor_id = parseInt(data.repartidor_id);
            data.activa = formData.has('activa');

            try {
                await api.rutas.create(data);
                showToast('Ruta creada exitosamente', 'success');
                closeModal();
                this.load();
            } catch (error) {
                showToast('Error al crear ruta: ' + error.message, 'error');
            }
        });
    },

    async showEditModal(id) {
        try {
            const ruta = await api.rutas.getById(id);
            const repartidoresOptions = this.repartidores.map(r => 
                `<option value="${r.id}" ${r.id === ruta.repartidor_id ? 'selected' : ''}>
                    ${r.nombre} ${r.apellido}
                </option>`
            ).join('');

            const content = `
                <form id="editRutaForm">
                    <div class="form-group">
                        <label>Nombre de la Ruta</label>
                        <input type="text" name="nombre" value="${ruta.nombre}" required>
                    </div>
                    <div class="form-group">
                        <label>Descripción</label>
                        <textarea name="descripcion" rows="2">${ruta.descripcion || ''}</textarea>
                    </div>
                    <div class="form-group">
                        <label>Zonas (separadas por coma)</label>
                        <input type="text" name="zonas" value="${ruta.zonas || ''}">
                    </div>
                    <div class="form-group">
                        <label>Hora Inicio</label>
                        <input type="time" name="hora_inicio" value="${ruta.hora_inicio || ''}">
                    </div>
                    <div class="form-group">
                        <label>Hora Fin</label>
                        <input type="time" name="hora_fin" value="${ruta.hora_fin || ''}">
                    </div>
                    <div class="form-group">
                        <label>Días Activos (separados por coma)</label>
                        <input type="text" name="dias_activos" value="${ruta.dias_activos || ''}">
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="activa" ${ruta.activa ? 'checked' : ''}>
                            Activa
                        </label>
                    </div>
                    <button type="submit" class="btn-primary">Actualizar</button>
                </form>
            `;

            createModal('Editar Ruta', content);

            document.getElementById('editRutaForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                data.activa = formData.has('activa');

                try {
                    await api.rutas.update(id, data);
                    showToast('Ruta actualizada exitosamente', 'success');
                    closeModal();
                    this.load();
                } catch (error) {
                    showToast('Error al actualizar: ' + error.message, 'error');
                }
            });
        } catch (error) {
            showToast('Error al cargar ruta: ' + error.message, 'error');
        }
    },

    async toggleActiva(id, activa) {
        try {
            await api.rutas.update(id, { activa });
            showToast(`Ruta ${activa ? 'activada' : 'desactivada'}`, 'success');
            this.load();
        } catch (error) {
            showToast('Error al actualizar ruta: ' + error.message, 'error');
        }
    },

    async delete(id) {
        if (!confirm('¿Estás seguro de eliminar esta ruta?')) return;

        try {
            await api.rutas.delete(id);
            showToast('Ruta eliminada exitosamente', 'success');
            this.load();
        } catch (error) {
            showToast('Error al eliminar: ' + error.message, 'error');
        }
    }
};
