import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { apiFetch, setToken } from '../api'

export default function RegisterPage() {
  const { t } = useTranslation()
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [age, setAge] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email,
          password,
          first_name: firstName,
          last_name: lastName,
          job_title: jobTitle || null,
          phone_number: phoneNumber || null,
          age: age ? Number(age) : null,
        }),
      })

      const resp = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      setToken(resp.access_token)
      nav('/', { replace: true })
    } catch (err: any) {
      setError(err?.message ?? t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="columns is-centered">
      <div className="column is-6">
        <div className="box opshub-fade-in animate__animated animate__fadeIn">
          <h1 className="title is-5">{t('auth.registerTitle')}</h1>
          <p className="subtitle is-6 has-text-grey">{t('auth.registerSubtitle')}</p>

          {error && <div className="notification is-danger is-light">{error}</div>}

          <form onSubmit={submit}>
            <div className="columns">
              <div className="column">
                <div className="field">
                  <label className="label">{t('auth.firstName')}</label>
                  <div className="control">
                    <input className="input" value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
                  </div>
                </div>
              </div>
              <div className="column">
                <div className="field">
                  <label className="label">{t('auth.lastName')}</label>
                  <div className="control">
                    <input className="input" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
                  </div>
                </div>
              </div>
            </div>

            <div className="field">
              <label className="label">{t('auth.email')}</label>
              <div className="control">
                <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
            </div>

            <div className="field">
              <label className="label">{t('auth.password')}</label>
              <div className="control">
                <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
              </div>
            </div>

            <div className="columns">
              <div className="column">
                <div className="field">
                  <label className="label">{t('auth.jobTitle')}</label>
                  <div className="control">
                    <input className="input" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} placeholder={t('common.optional')} />
                  </div>
                </div>
              </div>
              <div className="column">
                <div className="field">
                  <label className="label">{t('auth.phone')}</label>
                  <div className="control">
                    <input className="input" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} placeholder={t('common.optional')} />
                  </div>
                </div>
              </div>
              <div className="column is-3">
                <div className="field">
                  <label className="label">{t('auth.age')}</label>
                  <div className="control">
                    <input className="input" value={age} onChange={(e) => setAge(e.target.value)} inputMode="numeric" placeholder={t('common.optionalShort')} />
                  </div>
                </div>
              </div>
            </div>

            <div className="field is-grouped is-grouped-right">
              <div className="control">
                <button className={`button is-dark ${loading ? 'is-loading' : ''}`} type="submit">{t('auth.registerAction')}</button>
              </div>
            </div>
          </form>

          <p className="help">
            {t('auth.haveAccount')} <Link to="/login">{t('auth.goLogin')}</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
