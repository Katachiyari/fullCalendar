/**
 * Gestion de l'authentification côté client
 */

class Auth {
    constructor() {
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        const params = new URLSearchParams(window.location.search);
        this.debug = localStorage.getItem('debug') === '1' || params.get('debug') === '1';

        // Si activé via URL, persister
        if (params.get('debug') === '1') {
            localStorage.setItem('debug', '1');
        }
    }

    /**
     * Vérifier si l'utilisateur est connecté
     */
    isAuthenticated() {
        return !!this.token;
    }

    /**
     * Se déconnecter
     */
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.token = null;
        this.user = null;
        window.location.href = '/static/login.html';
    }

    /**
     * Récupérer le token JWT
     */
    getToken() {
        return this.token;
    }

    /**
     * Récupérer l'utilisateur actuel
     */
    getCurrentUser() {
        return this.user;
    }

    /**
     * Effectuer une requête API avec authentification
     */
    async fetch(url, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (this.debug) {
            console.debug('[auth.fetch]', options.method || 'GET', url, options.body ? { body: options.body } : '');
        }

        const response = await fetch(url, {
            ...options,
            headers
        });

        // Si 401, redirection vers login
        if (response.status === 401) {
            if (!this.debug) {
                this.logout();
                return null;
            }

            // En mode debug: ne pas rediriger, on laisse l'appelant afficher l'erreur
            console.warn('[auth.fetch] 401 received (debug mode): no redirect');
        }

        return response;
    }

    setDebug(enabled) {
        this.debug = !!enabled;
        localStorage.setItem('debug', this.debug ? '1' : '0');
    }

    /**
     * Met à jour les infos utilisateur
     */
    setUser(user) {
        this.user = user;
        localStorage.setItem('user', JSON.stringify(user));
    }

    /**
     * Met à jour le token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }
}

// Instance globale
const auth = new Auth();

// Vérifier la connexion au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    if (!auth.isAuthenticated() && !window.location.pathname.includes('login') && !window.location.pathname.includes('register')) {
        window.location.href = '/static/login.html';
    }
});
