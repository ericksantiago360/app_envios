// Main Application
const app = {
    init() {
        // Check authentication
        if (!auth.isAuthenticated()) {
            this.showLoginPage();
            auth.init();
            return;
        }

        // User is authenticated
        const user = auth.getCurrentUser();
        
        // Update UI
        this.updateUIForUser(user);
        
        // Initialize auth module
        auth.init();
        
        // Initialize all managers
        enviosManager.init();
        clientesManager.init();
        mapaManager.init();
        cotizadorManager.init();
        
        if (user.role === 'admin') {
            repartidoresManager.init();
            rutasManager.init();
        }
        
        // Setup navigation
        setupNavigation();
        
        // Show dashboard by default
        showPage('dashboardPage');
        loadDashboard();
    },

    showLoginPage() {
        // Hide navigation and user menu
        document.getElementById('mainNav').classList.add('nav-hidden');
        document.getElementById('userMenu').style.display = 'none';

        // Si viene desde la landing page con #registro, mostrar el formulario de registro
        const hash = window.location.hash; // ej: "#registro" o "#registro?role=repartidor"
        if (hash.startsWith('#registro')) {
            showPage('registerPage');

            // Si trae un rol sugerido (ej: #registro?role=repartidor), preseleccionarlo
            const queryPart = hash.split('?')[1];
            if (queryPart) {
                const params = new URLSearchParams(queryPart);
                const role = params.get('role');
                const roleSelect = document.getElementById('regRole');
                if (role && roleSelect) {
                    roleSelect.value = role;
                }
            }
        } else {
            // Show login page
            showPage('loginPage');
        }
    },

    updateUIForUser(user) {
        // Show navigation and user menu
        document.getElementById('mainNav').classList.remove('nav-hidden');
        document.getElementById('userMenu').style.display = 'flex';
        
        // Update user name
        document.getElementById('userName').textContent = user.full_name || user.username;
        
        // Update UI based on role
        updateUIForRole(user.role);
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
