// ============================================================
// cotizador.js — Widget de cotización de envíos EnvíosApp
// Conectado al endpoint POST /api/cotizacion/
// ============================================================

const cotizadorManager = {

    // ── Inicialización ──────────────────────────────────────
    init() {
        const btnCotizar = document.getElementById('btnAbrirCotizador');
        if (btnCotizar) {
            btnCotizar.addEventListener('click', () => {
                showPage('cotizadorPage');
                this.initForm();
            });
        }
        this.initForm();
    },

    initForm() {
        const form = document.getElementById('cotizadorForm');
        if (!form || form.dataset.initialized) return;
        form.dataset.initialized = 'true';

        // Selección visual de vehículo
        document.querySelectorAll('.veh-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.veh-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                document.getElementById('cotVehiculo').value = card.dataset.vehiculo;
                this.limpiarResultado();
            });
        });

        // Slider de distancia
        const sliderKm = document.getElementById('cotKm');
        if (sliderKm) {
            sliderKm.addEventListener('input', () => {
                document.getElementById('cotKmVal').textContent = sliderKm.value + ' km';
                this.limpiarResultado();
            });
        }

        // Slider de espera
        const sliderEspera = document.getElementById('cotEspera');
        if (sliderEspera) {
            sliderEspera.addEventListener('input', () => {
                document.getElementById('cotEsperaVal').textContent = sliderEspera.value + ' min';
                this.limpiarResultado();
            });
        }

        // Cambios en selects limpian resultado
        ['cotZonaOrigen', 'cotZonaDestino', 'cotServicio', 'cotPlan'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('change', () => this.limpiarResultado());
        });

        // Submit del formulario
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.calcular();
        });

        // Botón comparar planes
        const btnComparar = document.getElementById('btnCompararPlanes');
        if (btnComparar) {
            btnComparar.addEventListener('click', async () => {
                await this.compararPlanes();
            });
        }
    },

    // ── Recopilar datos del formulario ──────────────────────
    getFormData() {
        return {
            vehiculo:        document.getElementById('cotVehiculo').value,
            zona_origen:     document.getElementById('cotZonaOrigen').value,
            zona_destino:    document.getElementById('cotZonaDestino').value,
            distancia_km:    parseFloat(document.getElementById('cotKm').value),
            tipo_servicio:   document.getElementById('cotServicio').value,
            plan_repartidor: document.getElementById('cotPlan').value,
            espera_minutos:  parseInt(document.getElementById('cotEspera').value),
        };
    },

    // ── Calcular cotización ─────────────────────────────────
    async calcular() {
        const data = this.getFormData();
        if (!data.vehiculo) {
            showToast('Selecciona un tipo de vehículo', 'error');
            return;
        }

        const btn = document.getElementById('btnCotizar');
        btn.textContent = 'Calculando...';
        btn.disabled = true;

        try {
            const response = await fetch('/api/cotizacion/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Error al calcular');
            }

            this.mostrarResultado(result);

        } catch (error) {
            showToast('Error: ' + error.message, 'error');
        } finally {
            btn.textContent = '🧮 Calcular cotización';
            btn.disabled = false;
        }
    },

    // ── Comparar los 3 planes ───────────────────────────────
    async compararPlanes() {
        const data = this.getFormData();
        if (!data.vehiculo) {
            showToast('Selecciona un tipo de vehículo', 'error');
            return;
        }

        const btn = document.getElementById('btnCompararPlanes');
        btn.textContent = 'Comparando...';
        btn.disabled = true;

        try {
            const response = await fetch('/api/cotizacion/comparar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (!response.ok) {
                const errores = Array.isArray(result.detail)
                    ? result.detail.map(e => e.msg).join(', ')
                    : result.detail;
                throw new Error(errores);
            }

            this.mostrarComparacion(result);

        } catch (error) {
            showToast('Error: ' + error.message, 'error');
        } finally {
            btn.textContent = '📊 Comparar planes';
            btn.disabled = false;
        }
    },

    // ── Renderizar resultado principal ──────────────────────
    mostrarResultado(r) {
        const container = document.getElementById('cotizadorResultado');
        if (!container) return;

        if (!r.es_valida) {
            container.innerHTML = `
                <div class="cot-error">
                    <h4>⚠️ No se puede calcular la cotización</h4>
                    ${r.errores.map(e => `<p>${e}</p>`).join('')}
                </div>`;
            return;
        }

        const d = r.desglose;
        const dist = r.distribucion;
        const max = Math.max(d.tarifa_base, d.cargo_km, d.cargo_espera, d.cargo_servicio, d.cargo_zona, 1);

        const barras = [
            { label: 'Tarifa base',     valor: d.tarifa_base,    color: '#2563eb' },
            { label: 'Km adicionales',  valor: d.cargo_km,       color: '#3b82f6' },
            { label: 'Tiempo espera',   valor: d.cargo_espera,   color: '#60a5fa' },
            { label: 'Tipo servicio',   valor: d.cargo_servicio, color: '#10b981' },
            { label: 'Cruce de zona',   valor: d.cargo_zona,     color: '#f59e0b' },
        ].filter(b => b.valor > 0);

        container.innerHTML = `
            <div class="cot-result-card">

                <div class="cot-total-header">
                    <div>
                        <div class="cot-label">Precio al cliente</div>
                        <div class="cot-total-price">$${dist.total_cliente.toFixed(2)} <span>MXN</span></div>
                    </div>
                    <div class="cot-meta">
                        ${r.descripcion_ruta || ''}
                        ${r.tiempo_estimado_min ? `<br>⏱ ~${r.tiempo_estimado_min} min` : ''}
                        ${r.es_intermunicipal ? '<br>🔀 Envío intermunicipal' : ''}
                    </div>
                </div>

                <div class="cot-section-title">Desglose del precio</div>
                <div class="cot-barras">
                    ${barras.map(b => `
                        <div class="cot-barra-row">
                            <div class="cot-barra-label">${b.label}</div>
                            <div class="cot-barra-track">
                                <div class="cot-barra-fill" style="width:${Math.round(b.valor/max*100)}%;background:${b.color};"></div>
                            </div>
                            <div class="cot-barra-val">$${b.valor.toFixed(2)}</div>
                        </div>`).join('')}
                </div>

                <div class="cot-distribucion">
                    <div class="cot-dist-item cot-dist-rep">
                        <div class="cot-dist-label">Repartidor recibe</div>
                        <div class="cot-dist-amount">$${dist.ingreso_repartidor.toFixed(2)}</div>
                        <div class="cot-dist-pct">${(100 - dist.tasa_comision * 100).toFixed(0)}% del precio</div>
                    </div>
                    <div class="cot-dist-item cot-dist-plat">
                        <div class="cot-dist-label">Comisión plataforma</div>
                        <div class="cot-dist-amount">$${dist.comision_plataforma.toFixed(2)}</div>
                        <div class="cot-dist-pct">${(dist.tasa_comision * 100).toFixed(0)}% · Plan ${dist.plan_aplicado}</div>
                    </div>
                </div>

                ${r.advertencias && r.advertencias.length > 0 ? `
                    <div class="cot-advertencias">
                        ${r.advertencias.map(a => `<div class="cot-adv-item">⚠️ ${a}</div>`).join('')}
                    </div>` : ''}

                <div class="cot-actions">
                    <button class="btn-primary" onclick="showPage('enviosPage');enviosManager.load();">
                        📦 Crear envío con esta cotización
                    </button>
                    <button id="btnCompararPlanes" class="btn-secondary" onclick="cotizadorManager.compararPlanes();">
                        📊 Comparar planes
                    </button>
                </div>
            </div>`;
    },

    // ── Renderizar comparación de planes ────────────────────
    mostrarComparacion(r) {
        const container = document.getElementById('cotizadorResultado');
        if (!container) return;

        const planes = r.planes;
        const mejor = planes.reduce((a, b) =>
            a.neto_repartidor > b.neto_repartidor ? a : b
        );

        container.innerHTML = `
            <div class="cot-result-card">
                <div class="cot-section-title">Comparación de planes — $${r.precio_base.toFixed(2)} por entrega</div>

                <div class="cot-planes-grid">
                    ${planes.map(p => `
                        <div class="cot-plan-card ${p.plan === mejor.plan ? 'cot-plan-best' : ''}">
                            ${p.plan === mejor.plan ? '<div class="cot-plan-badge">★ Recomendado</div>' : ''}
                            <div class="cot-plan-nombre">${p.plan.toUpperCase()}</div>
                            <div class="cot-plan-membresia">$${p.membresia_mensual.toFixed(0)}/mes</div>
                            <div class="cot-plan-comision">${(p.tasa_comision * 100).toFixed(0)}% comisión</div>
                            <div class="cot-plan-neto">
                                <div class="cot-label">Tú recibes</div>
                                <div class="cot-plan-neto-val">$${p.neto_repartidor.toFixed(2)}</div>
                            </div>
                            <div class="cot-plan-plat">Plataforma: $${p.comision.toFixed(2)}</div>
                        </div>`).join('')}
                </div>

                <div class="cot-recomendacion">
                    💡 ${r.recomendacion}
                </div>

                <div class="cot-actions" style="margin-top:1rem;">
                    <button class="btn-secondary" onclick="cotizadorManager.calcular();">
                        ← Volver al desglose
                    </button>
                </div>
            </div>`;
    },

    // ── Limpiar resultado ───────────────────────────────────
    limpiarResultado() {
        const container = document.getElementById('cotizadorResultado');
        if (container) container.innerHTML = '';
    }
};
