// Authentication Module
const auth = {
    isAuthenticated() {
        return !!store.get('token');
    },

    getCurrentUser() {
        try {
            const user = store.get('user');
            return user ? JSON.parse(user) : null;
        } catch(e) {
            return null;
        }
    },

    async login(username, password) {
        const response = await api.auth.login(username, password);
        store.set('token', response.access_token);
        const user = await api.auth.getCurrentUser();
        store.set('user', JSON.stringify(user));
        return user;
    },

    async register(userData) {
        await api.auth.register(userData);
        return await this.login(userData.username, userData.password);
    },

    logout() {
        store.remove('token');
        store.remove('user');
        window.location.reload();
    },

    init() {
        const loginForm    = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        const logoutBtn    = document.getElementById('logoutBtn');
        const showRegister = document.getElementById('showRegister');
        const showLogin    = document.getElementById('showLogin');

        if (loginForm) {
            loginForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                const username = document.getElementById('loginUsername').value.trim();
                const password = document.getElementById('loginPassword').value;
                try {
                    await auth.login(username, password);
                    showToast('Inicio de sesión exitoso', 'success');
                    app.init();
                } catch (error) {
                    showToast(error.message || 'Usuario o contraseña incorrectos', 'error');
                }
            });
        }

        if (registerForm) {
            registerForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                const email = document.getElementById('regEmail').value.trim();
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    showToast('Ingresa un email válido (ej: usuario@dominio.com)', 'error');
                    return;
                }
                const userData = {
                    username:  document.getElementById('regUsername').value.trim(),
                    email:     email,
                    full_name: document.getElementById('regFullName').value.trim(),
                    role:      document.getElementById('regRole').value,
                    password:  document.getElementById('regPassword').value
                };
                try {
                    await auth.register(userData);
                    showToast('Registro exitoso', 'success');
                    app.init();
                } catch (error) {
                    showToast(error.message || 'Error al registrarse', 'error');
                }
            });
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', function() {
                auth.logout();
            });
        }

        if (showRegister) {
            showRegister.addEventListener('click', function(e) {
                e.preventDefault();
                showPage('registerPage');
            });
        }

        if (showLogin) {
            showLogin.addEventListener('click', function(e) {
                e.preventDefault();
                showPage('loginPage');
            });
        }
    }
};
