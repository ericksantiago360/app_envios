// Repartidores Manager
const repartidoresManager = {
    async init() {
        const btnNuevoRepartidor = document.getElementById('btnNuevoRepartidor');
        if (btnNuevoRepartidor) {
            btnNuevoRepartidor.addEventListener('click', () => this.showCreateModal());
        }
    },

    async load() {
        try {
            const repartidores = await api.repartidores.getAll();
            this.render(repartidores);
        } catch (error) {
            showToast('Error al cargar repartidores: ' + error.message, 'error');
        }
    },

    render(repartidores) {
        const container = document.getElementById('repartidoresList');
        
        if (repartidores.length === 0) {
            container.innerHTML = '<p class="text-center">No hay repartidores registrados</p>';
            return;
        }

        const rows = repartidores.map(repartidor => [
            repartidor.id,
            `${repartidor.nombre} ${repartidor.apellido}`,
            repartidor.telefono || '-',
            repartidor.vehiculo || '-',
            repartidor.placa_vehiculo || '-',
            repartidor.disponible ? 
                '<span class="badge badge-success">Disponible</span>' : 
                '<span class="badge badge-danger">No Disponible</span>',
            `
                <div class="action-buttons">
                    <button class="btn-icon" onclick="repartidoresManager.showEditModal(${repartidor.id})" title="Editar">✏️</button>
                    <button class="btn-icon" onclick="repartidoresManager.toggleDisponibilidad(${repartidor.id}, ${!repartidor.disponible})" title="Cambiar disponibilidad">
                        ${repartidor.disponible ? '🔴' : '🟢'}
                    </button>
                    ${auth.getCurrentUser().role === 'admin' ? 
                        `<button class="btn-icon" onclick="repartidoresManager.delete(${repartidor.id})" title="Eliminar">🗑️</button>` : 
                        ''}
                </div>
            `
        ]);

        container.innerHTML = createTable(
            ['ID', 'Nombre', 'Teléfono', 'Vehículo', 'Placa', 'Estado', 'Acciones'],
            rows
        );
    },

    showCreateModal() {
        const content = `
            <form id="repartidorForm">
                <div class="form-group">
                    <label>Nombre</label>
                    <input type="text" name="nombre" required>
                </div>
                <div class="form-group">
                    <label>Apellido</label>
                    <input type="text" name="apellido" required>
                </div>
                <div class="form-group">
                    <label>Teléfono</label>
                    <input type="tel" name="telefono">
                </div>
                <div class="form-group">
                    <label>Tipo de Vehículo</label>
                    <select name="vehiculo">
                        <option value="">Seleccionar...</option>
                        <option value="moto">Moto</option>
                        <option value="auto">Auto</option>
                        <option value="bicicleta">Bicicleta</option>
                        <option value="camioneta">Camioneta</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Placa del Vehículo</label>
                    <input type="text" name="placa_vehiculo">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="disponible" checked>
                        Disponible
                    </label>
                </div>
                <button type="submit" class="btn-primary">Crear Repartidor</button>
            </form>
        `;

        createModal('Nuevo Repartidor', content);

        document.getElementById('repartidorForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            data.disponible = formData.has('disponible');

            try {
                await api.repartidores.create(data);
                showToast('Repartidor creado exitosamente', 'success');
                closeModal();
                this.load();
            } catch (error) {
                showToast('Error al crear repartidor: ' + error.message, 'error');
            }
        });
    },

    async showEditModal(id) {
        try {
            const repartidor = await api.repartidores.getById(id);

            const content = `
                <form id="editRepartidorForm">
                    <div class="form-group">
                        <label>Nombre</label>
                        <input type="text" name="nombre" value="${repartidor.nombre}" required>
                    </div>
                    <div class="form-group">
                        <label>Apellido</label>
                        <input type="text" name="apellido" value="${repartidor.apellido}" required>
                    </div>
                    <div class="form-group">
                        <label>Teléfono</label>
                        <input type="tel" name="telefono" value="${repartidor.telefono || ''}">
                    </div>
                    <div class="form-group">
                        <label>Tipo de Vehículo</label>
                        <select name="vehiculo">
                            <option value="">Seleccionar...</option>
                            <option value="moto" ${repartidor.vehiculo === 'moto' ? 'selected' : ''}>Moto</option>
                            <option value="auto" ${repartidor.vehiculo === 'auto' ? 'selected' : ''}>Auto</option>
                            <option value="bicicleta" ${repartidor.vehiculo === 'bicicleta' ? 'selected' : ''}>Bicicleta</option>
                            <option value="camioneta" ${repartidor.vehiculo === 'camioneta' ? 'selected' : ''}>Camioneta</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Placa del Vehículo</label>
                        <input type="text" name="placa_vehiculo" value="${repartidor.placa_vehiculo || ''}">
                    </div>
                    <button type="submit" class="btn-primary">Actualizar</button>
                </form>
            `;

            createModal('Editar Repartidor', content);

            document.getElementById('editRepartidorForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);

                try {
                    await api.repartidores.update(id, data);
                    showToast('Repartidor actualizado exitosamente', 'success');
                    closeModal();
                    this.load();
                } catch (error) {
                    showToast('Error al actualizar: ' + error.message, 'error');
                }
            });
        } catch (error) {
            showToast('Error al cargar repartidor: ' + error.message, 'error');
        }
    },

    async toggleDisponibilidad(id, disponible) {
        try {
            await api.repartidores.update(id, { disponible });
            showToast('Disponibilidad actualizada', 'success');
            this.load();
        } catch (error) {
            showToast('Error al actualizar disponibilidad: ' + error.message, 'error');
        }
    },

    async delete(id) {
        if (!confirm('¿Estás seguro de eliminar este repartidor?')) return;

        try {
            await api.repartidores.delete(id);
            showToast('Repartidor eliminado exitosamente', 'success');
            this.load();
        } catch (error) {
            showToast('Error al eliminar: ' + error.message, 'error');
        }
    }
};
