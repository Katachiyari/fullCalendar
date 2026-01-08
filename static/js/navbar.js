/**
 * Composant navbar Bulma réutilisable
 */

function createNavbar(currentPage = 'calendar') {
    const navbar = document.querySelector('nav.navbar') || document.body.insertBefore(
        document.createElement('nav'),
        document.body.firstChild
    );

    navbar.classList.add('navbar');
    navbar.classList.add('is-transparent');
    navbar.setAttribute('role', 'navigation');
    navbar.setAttribute('aria-label', 'main navigation');

    const user = auth.getCurrentUser();
    const userName = user ? `${user.first_name} ${user.last_name}` : 'Utilisateur';

    navbar.innerHTML = `
        <div class="navbar-brand">
            <a class="navbar-item" href="/static/index.html">
                <span class="icon">
                    <i class="fas fa-calendar-alt"></i>
                </span>
                <strong>Calendrier</strong>
            </a>

            <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="navbarMenu">
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
            </a>
        </div>

        <div id="navbarMenu" class="navbar-menu">
            <div class="navbar-start">
                <a class="navbar-item ${currentPage === 'calendar' ? 'is-active' : ''}" href="/static/index.html">
                    <span class="icon"><i class="fas fa-home"></i></span>
                    <span>Accueil</span>
                </a>
            </div>

            <div class="navbar-end">
                <div class="navbar-item has-dropdown is-hoverable">
                    <a class="navbar-link">
                        <span class="icon"><i class="fas fa-user"></i></span>
                        <span>${userName}</span>
                    </a>

                    <div class="navbar-dropdown is-right">
                        <a class="navbar-item ${currentPage === 'profile' ? 'is-active' : ''}" href="/static/profile.html">
                            <span class="icon"><i class="fas fa-user-circle"></i></span>
                            <span>Mon Profil</span>
                        </a>
                        ${user && user.role === 'ADMIN' ? `
                            <a class="navbar-item ${currentPage === 'admin' ? 'is-active' : ''}" href="/static/admin-users.html">
                                <span class="icon"><i class="fas fa-users-cog"></i></span>
                                <span>Gestion Utilisateurs</span>
                            </a>
                            <hr class="navbar-divider">
                        ` : ''}
                        <a class="navbar-item" onclick="auth.logout()">
                            <span class="icon"><i class="fas fa-sign-out-alt"></i></span>
                            <span>Déconnexion</span>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Burger menu toggle
    const burger = navbar.querySelector('.navbar-burger');
    const menu = navbar.querySelector('#navbarMenu');
    burger.addEventListener('click', () => {
        burger.classList.toggle('is-active');
        menu.classList.toggle('is-active');
    });

    return navbar;
}

// Auto-initialiser si présence du navbar au chargement
document.addEventListener('DOMContentLoaded', () => {
    // Vérifier si on est pas sur les pages de login/register
    if (!window.location.pathname.includes('login') && !window.location.pathname.includes('register')) {
        // Créer la navbar si elle n'existe pas
        if (!document.querySelector('nav.navbar')) {
            createNavbar();
        }
    }
});
