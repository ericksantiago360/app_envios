// UI Utility Functions

// Escapar texto antes de insertarlo con innerHTML (previene XSS)
function escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Show page
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

// Create modal
function createModal(title, content) {
    const container = document.getElementById('modalContainer');
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="close-modal" onclick="closeModal()">×</button>
            </div>
            ${content}
        </div>
    `;
    
    container.innerHTML = '';
    container.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
}

// Close modal
function closeModal() {
    const container = document.getElementById('modalContainer');
    container.innerHTML = '';
}

// Format date
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(amount);
}

// Get estado badge
function getEstadoBadge(estado) {
    const badges = {
        'pendiente': '<span class="badge badge-warning">Pendiente</span>',
        'en_transito': '<span class="badge badge-info">En Tránsito</span>',
        'entregado': '<span class="badge badge-success">Entregado</span>',
        'cancelado': '<span class="badge badge-danger">Cancelado</span>'
    };
    return badges[estado] || '<span class="badge">' + escapeHtml(estado) + '</span>';
}

// Create table
function createTable(headers, rows) {
    let tableHTML = '<table><thead><tr>';
    
    headers.forEach(header => {
        tableHTML += `<th>${header}</th>`;
    });
    
    tableHTML += '</tr></thead><tbody>';
    
    rows.forEach(row => {
        tableHTML += '<tr>';
        row.forEach(cell => {
            tableHTML += `<td>${cell}</td>`;
        });
        tableHTML += '</tr>';
    });
    
    tableHTML += '</tbody></table>';
    
    return tableHTML;
}

// Setup navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('nav a[data-page]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.getAttribute('data-page');
            showPage(page + 'Page');
            
            // Load page data
            if (page === 'dashboard') {
                loadDashboard();
            } else if (page === 'cotizador') {
                cotizadorManager.initForm();
            } else if (page === 'mapa') {
                mapaManager.load();
            } else if (page === 'envios') {
                enviosManager.load();
            } else if (page === 'clientes') {
                clientesManager.load();
            } else if (page === 'repartidores') {
                repartidoresManager.load();
            } else if (page === 'rutas') {
                rutasManager.load();
            }
        });
    });
}

// Update UI based on user role
function updateUIForRole(role) {
    const adminElements = document.querySelectorAll('.admin-only');

    if (role === 'admin') {
        adminElements.forEach(el => {
            // Forzar display correcto segun tipo de elemento
            // para sobreescribir el CSS .admin-only { display: none }
            if (el.tagName === 'LI') {
                el.style.display = 'list-item';
            } else if (el.tagName === 'DIV') {
                el.style.display = 'block';
            } else {
                el.style.display = 'block';
            }
        });
    } else {
        adminElements.forEach(el => {
            el.style.display = 'none';
        });
    }
}

// Load dashboard
async function loadDashboard() {
    try {
        // Cargar envios y clientes en paralelo
        const [envios, clientes] = await Promise.all([
            api.envios.getAll(),
            api.clientes.getAll()
        ]);

        // Stats de envios
        document.getElementById('totalEnvios').textContent = envios.length;
        document.getElementById('enviosTransito').textContent =
            envios.filter(e => e.estado === 'en_transito').length;
        document.getElementById('enviosEntregados').textContent =
            envios.filter(e => e.estado === 'entregado').length;
        document.getElementById('enviosPendientes').textContent =
            envios.filter(e => e.estado === 'pendiente').length;

        // Stat de clientes (si existe el elemento)
        const elClientes = document.getElementById('totalClientes');
        if (elClientes) elClientes.textContent = clientes.length;

        // Envios recientes
        const recent = envios.slice(0, 5);
        const container = document.getElementById('recentEnvios');

        if (recent.length === 0) {
            container.innerHTML = '<p class="text-center" style="padding:1.5rem;">No hay env\u00edos a\u00fan. <a href="#" onclick="showPage(&quot;enviosPage&quot;);enviosManager.load();">Crear primer env\u00edo</a></p>';
        } else {
            const rows = recent.map(envio => [
                escapeHtml(envio.numero_guia),
                escapeHtml(envio.ciudad_origen + ' → ' + envio.ciudad_destino),
                getEstadoBadge(envio.estado),
                formatDate(envio.fecha_creacion),
                formatCurrency(envio.costo)
            ]);
            container.innerHTML = createTable(
                ['Guía', 'Ruta', 'Estado', 'Fecha', 'Costo'],
                rows
            );
        }

        // Clientes recientes
        const recentClientes = clientes.slice(-3).reverse();
        const contClientes = document.getElementById('recentClientes');
        if (contClientes) {
            if (recentClientes.length === 0) {
                contClientes.innerHTML = '<p class="text-center" style="padding:1rem;">Sin clientes registrados aún.</p>';
            } else {
                const rowsCli = recentClientes.map(c => [
                    c.id,
                    escapeHtml(`${c.nombre} ${c.apellido}`),
                    escapeHtml(c.telefono || '-'),
                    escapeHtml(c.ciudad || '-')
                ]);
                contClientes.innerHTML = createTable(
                    ['ID', 'Nombre', 'Teléfono', 'Ciudad'],
                    rowsCli
                );
            }
        }

    } catch (error) {
        showToast('Error al cargar dashboard: ' + error.message, 'error');
    }
}
