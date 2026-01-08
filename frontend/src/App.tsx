import { useState } from 'react'
import { NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import DashboardPage from './pages/DashboardPage'
import CalendarPage from './pages/CalendarPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import AdminUsersPage from './pages/AdminUsersPage'
import ServerPage from './pages/ServerPage'
import AnsiblePage from './pages/AnsiblePage'
import { getToken, setToken } from './api'
import { useMe } from './hooks/useMe'

type Theme = 'dark' | 'bright'

function getTheme(): Theme {
  const attr = document.documentElement.getAttribute('data-theme')
  return attr === 'bright' ? 'bright' : 'dark'
}

function setTheme(theme: Theme) {
  document.documentElement.setAttribute('data-theme', theme)
  try {
    localStorage.setItem('opshub_theme', theme)
  } catch {
    // best-effort
  }
}

function RequireAuth({ children }: { children: JSX.Element }) {
  const location = useLocation()
  const token = getToken()
  if (!token) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}

export default function App() {
  const { t, i18n } = useTranslation()
  const { me } = useMe()

  const [theme, setThemeState] = useState<Theme>(() => getTheme())

  function toggleTheme() {
    const next: Theme = theme === 'dark' ? 'bright' : 'dark'
    setTheme(next)
    setThemeState(next)
  }

  return (
    <div className="opshub-app">
      <nav className="navbar opshub-navbar" role="navigation" aria-label="main navigation">
        <div className="navbar-brand">
          <a className="navbar-item" href="/">
            <strong>{t('appName')}</strong>
          </a>
        </div>

        <div className="navbar-menu is-active">
          <div className="navbar-start">
            <NavLink className={({ isActive }) => `navbar-item ${isActive ? 'is-active has-text-weight-semibold' : ''}`} to="/">{t('nav.dashboard')}</NavLink>
            <a className="navbar-item" href="/kanban/">{t('nav.kanban')}</a>
            <NavLink className={({ isActive }) => `navbar-item ${isActive ? 'is-active has-text-weight-semibold' : ''}`} to="/calendar">{t('nav.calendar')}</NavLink>

            <NavLink className={({ isActive }) => `navbar-item ${isActive ? 'is-active has-text-weight-semibold' : ''}`} to="/ansible">{t('nav.ansible')}</NavLink>
            {me?.role === 'ADMIN' && (
              <>
                <NavLink className={({ isActive }) => `navbar-item ${isActive ? 'is-active has-text-weight-semibold' : ''}`} to="/server">{t('nav.server')}</NavLink>
                <NavLink className={({ isActive }) => `navbar-item ${isActive ? 'is-active has-text-weight-semibold' : ''}`} to="/admin/users">{t('nav.admin')}</NavLink>
              </>
            )}
            <NavLink className={({ isActive }) => `navbar-item ${isActive ? 'is-active has-text-weight-semibold' : ''}`} to="/profile">{t('nav.profile')}</NavLink>
          </div>

          <div className="navbar-end">
            <div className="navbar-item">
              <div className="buttons">
                <button className="button is-light" onClick={() => void i18n.changeLanguage(i18n.language === 'fr' ? 'en' : 'fr')}>FR/EN</button>
                <button className="button is-light" onClick={toggleTheme}>
                  {t('nav.theme')}: {t(`theme.${theme}`)}
                </button>
                <button
                  className="button is-dark"
                  onClick={() => {
                    setToken(null)
                    window.location.href = '/login'
                  }}
                >
                  {t('nav.logout')}
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="section opshub-main">
        <div className="opshub-container">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/" element={<RequireAuth><DashboardPage /></RequireAuth>} />
            <Route path="/calendar" element={<RequireAuth><CalendarPage /></RequireAuth>} />
            <Route path="/ansible" element={<RequireAuth><AnsiblePage /></RequireAuth>} />
            <Route path="/server" element={<RequireAuth><ServerPage /></RequireAuth>} />
            <Route path="/admin/users" element={<RequireAuth><AdminUsersPage /></RequireAuth>} />
            <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
          </Routes>
        </div>
      </main>
    </div>
  )
}
