// Clientes Manager
const clientesManager = {
    async init() {
        const btnNuevoCliente = document.getElementById('btnNuevoCliente');
        if (btnNuevoCliente) {
            btnNuevoCliente.addEventListener('click', () => this.showCreateModal());
        }
    },

    async load() {
        try {
            const clientes = await api.clientes.getAll();
            this.render(clientes);
        } catch (error) {
            showToast('Error al cargar clientes: ' + error.message, 'error');
        }
    },

    render(clientes) {
        const container = document.getElementById('clientesList');
        
        if (clientes.length === 0) {
            container.innerHTML = '<p class="text-center">No hay clientes registrados</p>';
            return;
        }

        const rows = clientes.map(cliente => [
            cliente.id,
            escapeHtml(`${cliente.nombre} ${cliente.apellido}`),
            escapeHtml(cliente.telefono || '-'),
            escapeHtml(cliente.ciudad || '-'),
            escapeHtml(cliente.direccion || '-'),
            `
                <div class="action-buttons">
                    <button class="btn-icon" onclick="clientesManager.showEditModal(${cliente.id})" title="Editar">✏️</button>
                    ${auth.getCurrentUser().role === 'admin' ? 
                        `<button class="btn-icon" onclick="clientesManager.delete(${cliente.id})" title="Eliminar">🗑️</button>` : 
                        ''}
                </div>
            `
        ]);

        container.innerHTML = createTable(
            ['ID', 'Nombre', 'Teléfono', 'Ciudad', 'Dirección', 'Acciones'],
            rows
        );
    },

    showCreateModal() {
        const content = `
            <form id="clienteForm">
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
                    <label>Dirección</label>
                    <input type="text" name="direccion">
                </div>
                <div class="form-group">
                    <label>Ciudad</label>
                    <input type="text" name="ciudad">
                </div>
                <div class="form-group">
                    <label>Código Postal</label>
                    <input type="text" name="codigo_postal">
                </div>
                <button type="submit" class="btn-primary">Crear Cliente</button>
            </form>
        `;

        createModal('Nuevo Cliente', content);

        document.getElementById('clienteForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            try {
                await api.clientes.create(data);
                showToast('Cliente creado exitosamente', 'success');
                closeModal();
                this.load();
            } catch (error) {
                showToast('Error al crear cliente: ' + error.message, 'error');
            }
        });
    },

    async showEditModal(id) {
        try {
            const cliente = await api.clientes.getById(id);

            const content = `
                <form id="editClienteForm">
                    <div class="form-group">
                        <label>Nombre</label>
                        <input type="text" name="nombre" value="${escapeHtml(cliente.nombre)}" required>
                    </div>
                    <div class="form-group">
                        <label>Apellido</label>
                        <input type="text" name="apellido" value="${escapeHtml(cliente.apellido)}" required>
                    </div>
                    <div class="form-group">
                        <label>Teléfono</label>
                        <input type="tel" name="telefono" value="${escapeHtml(cliente.telefono)}">
                    </div>
                    <div class="form-group">
                        <label>Dirección</label>
                        <input type="text" name="direccion" value="${escapeHtml(cliente.direccion)}">
                    </div>
                    <div class="form-group">
                        <label>Ciudad</label>
                        <input type="text" name="ciudad" value="${escapeHtml(cliente.ciudad)}">
                    </div>
                    <div class="form-group">
                        <label>Código Postal</label>
                        <input type="text" name="codigo_postal" value="${escapeHtml(cliente.codigo_postal)}">
                    </div>
                    <button type="submit" class="btn-primary">Actualizar</button>
                </form>
            `;

            createModal('Editar Cliente', content);

            document.getElementById('editClienteForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);

                try {
                    await api.clientes.update(id, data);
                    showToast('Cliente actualizado exitosamente', 'success');
                    closeModal();
                    this.load();
                } catch (error) {
                    showToast('Error al actualizar: ' + error.message, 'error');
                }
            });
        } catch (error) {
            showToast('Error al cargar cliente: ' + error.message, 'error');
        }
    },

    async delete(id) {
        if (!confirm('¿Estás seguro de eliminar este cliente?')) return;

        try {
            await api.clientes.delete(id);
            showToast('Cliente eliminado exitosamente', 'success');
            this.load();
        } catch (error) {
            showToast('Error al eliminar: ' + error.message, 'error');
        }
    }
};
