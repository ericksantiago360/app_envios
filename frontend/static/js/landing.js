// ===== Landing Page JS =====

const API_BASE = '/api';

// ---- Mobile menu ----
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('mobileMenuToggle');
    const menu = document.getElementById('landingMenu');

    if (toggle && menu) {
        toggle.addEventListener('click', () => {
            menu.classList.toggle('open');
        });

        // Cerrar menú al hacer clic en un link
        menu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => menu.classList.remove('open'));
        });
    }

    initTracking();
    initVehicleTabs();
});

// ===== Rastreo de envíos (conectado a la API real) =====
function initTracking() {
    const form = document.getElementById('trackingForm');
    const input = document.getElementById('trackingInput');
    const resultBox = document.getElementById('trackingResult');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const guia = input.value.trim();
        if (!guia) return;

        resultBox.className = 'tracking-result show';
        resultBox.innerHTML = '<p>Buscando tu envío...</p>';

        try {
            const response = await fetch(`${API_BASE}/envios/tracking/${encodeURIComponent(guia)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'No se encontró el envío');
            }

            mostrarResultadoTracking(data);
        } catch (error) {
            resultBox.className = 'tracking-result show error';
            resultBox.innerHTML = `
                <strong>⚠️ No pudimos encontrar ese envío</strong>
                <p style="margin-top:0.5rem; font-size:0.9rem;">
                    Verifica el número de guía e intenta nuevamente. Si el problema persiste,
                    <a href="app.html" style="color:#991b1b; font-weight:600;">inicia sesión</a> para ver el detalle completo.
                </p>
            `;
        }
    });
}

function mostrarResultadoTracking(envio) {
    const resultBox = document.getElementById('trackingResult');

    const estadoLabels = {
        'pendiente': '⏳ Pendiente',
        'en_transito': '🚚 En tránsito',
        'entregado': '✅ Entregado',
        'cancelado': '❌ Cancelado'
    };

    const fecha = envio.fecha_creacion
        ? new Date(envio.fecha_creacion).toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' })
        : '-';

    resultBox.className = 'tracking-result show success';
    resultBox.innerHTML = `
        <div class="tracking-result-row">
            <span>Número de guía</span>
            <strong>${envio.numero_guia}</strong>
        </div>
        <div class="tracking-result-row">
            <span>Estado</span>
            <strong>${estadoLabels[envio.estado] || envio.estado}</strong>
        </div>
        <div class="tracking-result-row">
            <span>Origen</span>
            <strong>${envio.ciudad_origen}</strong>
        </div>
        <div class="tracking-result-row">
            <span>Destino</span>
            <strong>${envio.ciudad_destino}</strong>
        </div>
        <div class="tracking-result-row">
            <span>Fecha de creación</span>
            <strong>${fecha}</strong>
        </div>
        <p style="margin-top:0.85rem; font-size:0.85rem;">
            <a href="app.html" style="color:#2563eb; font-weight:600;">Inicia sesión</a> para ver el mapa en vivo y más detalles.
        </p>
    `;
}

// ===== Tabs de vehículos / tarifas =====
const VEHICULOS = [
    {
        id: 'moto',
        icon: '🛵',
        nombre: 'Motocicleta',
        peso: 'Hasta 20 kg',
        tamano: '40 × 40 × 35 cm',
        ideal: 'Documentos, paquetes pequeños, alimentos y bebidas',
        nota: 'La tarifa final puede variar según distancia, tráfico y disponibilidad de repartidores.'
    },
    {
        id: 'hatchback',
        icon: '🚗',
        nombre: 'Hatchback',
        peso: 'Hasta 100 kg',
        tamano: '90 × 90 × 70 cm',
        ideal: 'Paquetería mediana, más económico que un auto',
        nota: 'La tarifa final puede variar según distancia, tráfico y disponibilidad de repartidores.'
    },
    {
        id: 'auto',
        icon: '🚙',
        nombre: 'Auto',
        peso: 'Hasta 200 kg',
        tamano: '125 × 80 × 60 cm',
        ideal: 'Paquetes medianos, electrónicos, electrodomésticos pequeños',
        nota: 'La tarifa final puede variar según distancia, tráfico y disponibilidad de repartidores.'
    },
    {
        id: 'suv',
        icon: '🚐',
        nombre: 'SUV',
        peso: 'Hasta 300 kg',
        tamano: '130 × 160 × 80 cm',
        ideal: 'Varios tamaños de paquetes y múltiples entregas',
        nota: 'La tarifa final puede variar según distancia, tráfico y disponibilidad de repartidores.'
    },
    {
        id: 'pickup',
        icon: '🛻',
        nombre: 'Pick up',
        peso: 'Hasta 700 kg',
        tamano: '168 × 134 × 51 cm',
        ideal: 'Objetos grandes y pesados, más económico que una camioneta',
        nota: 'La tarifa final puede variar según distancia, tráfico y disponibilidad de repartidores.'
    },
    {
        id: 'camioneta',
        icon: '🚚',
        nombre: 'Camioneta',
        peso: 'Hasta 500 kg',
        tamano: '188 × 133 × 108 cm',
        ideal: 'Electrodomésticos, muebles, instrumentos musicales',
        nota: 'La tarifa final puede variar según distancia, tráfico y disponibilidad de repartidores.'
    },
    {
        id: 'camion',
        icon: '🚛',
        nombre: 'Camión',
        peso: 'Hasta 1.5 ton',
        tamano: '200 × 200 × 170 cm',
        ideal: 'Mercancía grande y voluminosa, mudanzas, ferretería',
        nota: 'La tarifa final puede variar según distancia, tráfico y disponibilidad de repartidores.'
    }
];

function initVehicleTabs() {
    const tabsContainer = document.getElementById('vehicleTabs');
    const detailContainer = document.getElementById('vehicleDetail');
    if (!tabsContainer || !detailContainer) return;

    tabsContainer.innerHTML = VEHICULOS.map((v, i) => `
        <div class="vehicle-tab ${i === 0 ? 'active' : ''}" data-id="${v.id}">
            <span class="v-icon">${v.icon}</span>
            <span class="v-name">${v.nombre}</span>
        </div>
    `).join('');

    function renderDetail(vehiculo) {
        detailContainer.innerHTML = `
            <div class="vehicle-detail-icon">${vehiculo.icon}</div>
            <div>
                <h3 style="font-size:1.4rem; margin-bottom:1rem;">${vehiculo.nombre}</h3>
                <div class="vehicle-detail-grid">
                    <div class="vehicle-spec">
                        <div class="label">Límite de peso</div>
                        <div class="value">${vehiculo.peso}</div>
                    </div>
                    <div class="vehicle-spec">
                        <div class="label">Tamaño máx. (L×A×A)</div>
                        <div class="value">${vehiculo.tamano}</div>
                    </div>
                    <div class="vehicle-spec" style="grid-column: 1 / -1;">
                        <div class="label">Ideal para</div>
                        <div class="value">${vehiculo.ideal}</div>
                    </div>
                </div>
                <p style="margin-top:1.25rem; font-size:0.8rem; color: var(--text-secondary);">${vehiculo.nota}</p>
                <a href="app.html#registro" class="btn-cta" style="margin-top:1.25rem; display:inline-block;">Solicitar este vehículo</a>
            </div>
        `;
    }

    renderDetail(VEHICULOS[0]);

    tabsContainer.querySelectorAll('.vehicle-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            tabsContainer.querySelectorAll('.vehicle-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const vehiculo = VEHICULOS.find(v => v.id === tab.dataset.id);
            renderDetail(vehiculo);
        });
    });
}
