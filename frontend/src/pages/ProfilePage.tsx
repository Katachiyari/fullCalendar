import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import { useMe } from '../hooks/useMe'
import { useTranslation } from 'react-i18next'

export default function ProfilePage() {
  const { t } = useTranslation()
  const { me, loading, error, reload } = useMe()
  const [edit, setEdit] = useState(false)

  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [age, setAge] = useState('')

  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [saveOk, setSaveOk] = useState<string | null>(null)

  useEffect(() => {
    if (!me) return
    setFirstName(me.first_name ?? '')
    setLastName(me.last_name ?? '')
    setJobTitle(me.job_title ?? '')
    setPhoneNumber(me.phone_number ?? '')
    setAge(me.age != null ? String(me.age) : '')
  }, [me])

  async function save() {
    setSaveError(null)
    setSaveOk(null)
    setSaving(true)
    try {
      await apiFetch('/auth/me', {
        method: 'PUT',
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          job_title: jobTitle || null,
          phone_number: phoneNumber || null,
          age: age ? Number(age) : null,
        }),
      })
      setSaveOk(t('profile.updated'))
      setEdit(false)
      await reload()
    } catch (e: any) {
      setSaveError(e?.message ?? t('common.error'))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <progress className="progress is-small is-dark" max={100}>{t('common.loading')}</progress>
  if (error) return <div className="notification is-danger is-light">{error}</div>
  if (!me) return <div className="notification is-warning is-light">{t('profile.notAuthenticated')}</div>

  return (
    <div className="opshub-fade-in animate__animated animate__fadeIn">
      <div className="columns">
        <div className="column is-5">
          <div className="box">
            <h1 className="title is-5">{t('profile.title')}</h1>

            {saveError && <div className="notification is-danger is-light">{saveError}</div>}
            {saveOk && <div className="notification is-success is-light">{saveOk}</div>}

            <div className="content is-small">
              <p><strong>{t('auth.email')}:</strong> {me.email}</p>
              <p><strong>{t('profile.role')}:</strong> {me.role}</p>
              <p><strong>{t('profile.group')}:</strong> {me.group?.name ?? t('common.dash')}</p>
              <p><strong>{t('profile.emailVerified')}:</strong> {me.email_verified ? t('common.yes') : t('common.no')}</p>
              <p><strong>{t('profile.active')}:</strong> {me.is_active ? t('common.yes') : t('common.no')}</p>
            </div>

            {!edit && (
              <div className="buttons">
                <button className="button is-dark" onClick={() => setEdit(true)}>{t('common.edit')}</button>
              </div>
            )}

            {edit && (
              <div>
                <div className="columns">
                  <div className="column">
                    <div className="field">
                      <label className="label">{t('auth.firstName')}</label>
                      <div className="control"><input className="input" value={firstName} onChange={(e) => setFirstName(e.target.value)} /></div>
                    </div>
                  </div>
                  <div className="column">
                    <div className="field">
                      <label className="label">{t('auth.lastName')}</label>
                      <div className="control"><input className="input" value={lastName} onChange={(e) => setLastName(e.target.value)} /></div>
                    </div>
                  </div>
                </div>

                <div className="columns">
                  <div className="column">
                    <div className="field">
                      <label className="label">{t('auth.jobTitle')}</label>
                      <div className="control"><input className="input" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} /></div>
                    </div>
                  </div>
                  <div className="column">
                    <div className="field">
                      <label className="label">{t('auth.phone')}</label>
                      <div className="control"><input className="input" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} /></div>
                    </div>
                  </div>
                  <div className="column is-3">
                    <div className="field">
                      <label className="label">{t('auth.age')}</label>
                      <div className="control"><input className="input" value={age} onChange={(e) => setAge(e.target.value)} inputMode="numeric" /></div>
                    </div>
                  </div>
                </div>

                <div className="field is-grouped is-grouped-right">
                  <div className="control"><button className="button is-light" onClick={() => setEdit(false)} disabled={saving}>{t('common.cancel')}</button></div>
                  <div className="control"><button className={`button is-dark ${saving ? 'is-loading' : ''}`} onClick={() => void save()}>{t('common.save')}</button></div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="column">
          <div className="box">
            <h2 className="title is-6">{t('common.actions')}</h2>
            <div className="buttons">
              <button
                className="button is-light"
                onClick={() => {
                  void apiFetch('/auth/request-email-verification', { method: 'POST' })
                    .then(() => alert(t('profile.requestSent')))
                    .catch((e: any) => alert(e?.message ?? t('common.error')))
                }}
              >
                {t('profile.verifyEmail')}
              </button>
            </div>
            <p className="help">{t('profile.verifyHelp')}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
