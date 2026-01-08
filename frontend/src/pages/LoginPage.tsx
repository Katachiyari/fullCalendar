import { useState } from 'react'
import { apiFetch, setToken } from '../api'
import { useTranslation } from 'react-i18next'

export default function LoginPage() {
  const { t } = useTranslation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      if (!data?.access_token) throw new Error(t('auth.loginFailed'))
      setToken(data.access_token)
      window.location.href = '/'
    } catch (e: any) {
      setError(e?.message ?? t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="opshub-container opshub-fade-in animate__animated animate__fadeIn">
      <section className="section">
        <div className="columns is-centered">
          <div className="column is-5">
            <div className="box">
              <h1 className="title is-4">{t('auth.loginTitle')}</h1>
              <p className="subtitle is-6 has-text-grey">{t('auth.loginSubtitle')}</p>

              {error && <div className="notification is-danger is-light">{error}</div>}

              <form onSubmit={submit}>
                <div className="field">
                  <label className="label">{t('auth.email')}</label>
                  <div className="control">
                    <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                  </div>
                </div>

                <div className="field">
                  <label className="label">{t('auth.password')}</label>
                  <div className="control">
                    <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                  </div>
                </div>

                <div className="field is-grouped is-grouped-right">
                  <p className="control">
                    <button className={`button is-link ${loading ? 'is-loading' : ''}`} type="submit">{t('auth.loginAction')}</button>
                  </p>
                </div>
              </form>

              <hr />
              <div className="content is-size-7">
                <p>
                  {t('auth.adminDefault')}: <strong>admin@devops.example.com</strong> / <strong>Admin@123456</strong>
                </p>
                <p>
                  {t('auth.noAccount')} <a href="/register">{t('auth.goRegister')}</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
