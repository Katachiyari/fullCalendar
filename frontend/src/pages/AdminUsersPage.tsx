import { useEffect, useMemo, useRef, useState } from 'react'
import { apiFetch } from '../api'
import { useMe } from '../hooks/useMe'
import { useTranslation } from 'react-i18next'

type User = {
  id: string
  email: string
  first_name: string
  last_name: string
  phone_number?: string | null
  age?: number | null
  job_title?: string | null
  role: 'ADMIN' | 'MODERATOR' | 'USER'
  is_active: boolean
  email_verified: boolean
  group_id?: string | null
}

type Group = { id: string; slug: string; name: string }

export default function AdminUsersPage() {
  const { t } = useTranslation()
  const { me, loading: meLoading, error: meError } = useMe()
  const aliveRef = useRef(true)
  const [users, setUsers] = useState<User[]>([])
  const [groups, setGroups] = useState<Group[]>([])
  const [q, setQ] = useState('')

  const [selectedId, setSelectedId] = useState<string | null>(null)
  const selected = useMemo(() => users.find(u => u.id === selectedId) ?? null, [users, selectedId])

  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [dataLoading, setDataLoading] = useState(false)

  // Create form
  const [cEmail, setCEmail] = useState('')
  const [cPassword, setCPassword] = useState('')
  const [cFirst, setCFirst] = useState('')
  const [cLast, setCLast] = useState('')
  const [cRole, setCRole] = useState<User['role']>('USER')

  // Edit form
  const [eFirst, setEFirst] = useState('')
  const [eLast, setELast] = useState('')
  const [eRole, setERole] = useState<User['role']>('USER')
  const [eActive, setEActive] = useState(true)
  const [eVerified, setEVerified] = useState(true)
  const [eGroupId, setEGroupId] = useState<string>('')
  const [ePassword, setEPassword] = useState('')

  async function load() {
    setError(null)
    setDataLoading(true)
    try {
      const [u, g] = await Promise.all([
        apiFetch('/users/?limit=200'),
        apiFetch('/groups/'),
      ])
      if (!aliveRef.current) return
      setUsers(u)
      setGroups(g)
    } finally {
      if (!aliveRef.current) return
      setDataLoading(false)
    }
  }

  useEffect(() => {
    aliveRef.current = true
    return () => {
      aliveRef.current = false
    }
  }, [])

  useEffect(() => {
    if (meLoading) return
    if (!me || me.role !== 'ADMIN') return

    void load().catch((e: any) => {
      if (!aliveRef.current) return
      setError(e?.message ?? t('common.error'))
    })
  }, [meLoading, me])

  useEffect(() => {
    if (!selected) return
    setEFirst(selected.first_name)
    setELast(selected.last_name)
    setERole(selected.role)
    setEActive(!!selected.is_active)
    setEVerified(!!selected.email_verified)
    setEGroupId(selected.group_id ?? '')
    setEPassword('')
  }, [selected])

  const filtered = useMemo(() => {
    const t = q.trim().toLowerCase()
    if (!t) return users
    return users.filter(u => `${u.email} ${u.first_name} ${u.last_name}`.toLowerCase().includes(t))
  }, [q, users])

  if (meLoading) return <progress className="progress is-small is-dark" max={100}>{t('common.loading')}</progress>
  if (meError) return <div className="notification is-danger is-light">{meError}</div>
  if (!me || me.role !== 'ADMIN') return <div className="notification is-warning is-light">{t('admin.accessRequired')}</div>

  return (
    <div className="opshub-fade-in animate__animated animate__fadeIn">
      <div className="level">
        <div className="level-left">
          <h1 className="title is-5 mb-0">{t('admin.usersTitle')}</h1>
        </div>
        <div className="level-right">
          <button className={`button is-dark ${dataLoading ? 'is-loading' : ''}`} onClick={() => void load()}>{t('common.refresh')}</button>
        </div>
      </div>

      {dataLoading && users.length === 0 && (
        <progress className="progress is-small is-dark" max={100}>{t('common.loading')}</progress>
      )}

      {error && <div className="notification is-danger is-light">{error}</div>}

      <div className="box">
        <h2 className="title is-6">{t('admin.createUser')}</h2>
        <div className="columns is-multiline">
          <div className="column is-4">
            <div className="field">
              <label className="label">{t('auth.email')}</label>
              <div className="control"><input className="input" value={cEmail} onChange={(e) => setCEmail(e.target.value)} /></div>
            </div>
          </div>
          <div className="column is-4">
            <div className="field">
              <label className="label">{t('auth.password')}</label>
              <div className="control"><input className="input" type="password" value={cPassword} onChange={(e) => setCPassword(e.target.value)} /></div>
            </div>
          </div>
          <div className="column is-2">
            <div className="field">
              <label className="label">{t('admin.role')}</label>
              <div className="control">
                <div className="select is-fullwidth">
                  <select value={cRole} onChange={(e) => setCRole(e.target.value as any)}>
                    <option value="USER">USER</option>
                    <option value="MODERATOR">MODERATOR</option>
                    <option value="ADMIN">ADMIN</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div className="column is-6">
            <div className="field">
              <label className="label">{t('auth.firstName')}</label>
              <div className="control"><input className="input" value={cFirst} onChange={(e) => setCFirst(e.target.value)} /></div>
            </div>
          </div>
          <div className="column is-6">
            <div className="field">
              <label className="label">{t('auth.lastName')}</label>
              <div className="control"><input className="input" value={cLast} onChange={(e) => setCLast(e.target.value)} /></div>
            </div>
          </div>
        </div>

        <div className="field is-grouped is-grouped-right">
          <div className="control">
            <button
              className={`button is-dark ${busy ? 'is-loading' : ''}`}
              disabled={!cEmail || !cPassword || !cFirst || !cLast}
              onClick={() => {
                setBusy(true)
                setError(null)
                void apiFetch('/users/', {
                  method: 'POST',
                  body: JSON.stringify({
                    email: cEmail,
                    password: cPassword,
                    first_name: cFirst,
                    last_name: cLast,
                    role: cRole,
                  }),
                })
                  .then(() => load())
                  .then(() => {
                    setCEmail('')
                    setCPassword('')
                    setCFirst('')
                    setCLast('')
                    setCRole('USER')
                  })
                  .catch((e: any) => setError(e?.message ?? t('common.error')))
                  .finally(() => setBusy(false))
              }}
            >
              {t('common.create')}
            </button>
          </div>
        </div>
      </div>

      <div className="columns">
        <div className="column is-7">
          <div className="box">
            <div className="field">
              <label className="label">{t('admin.search')}</label>
              <div className="control"><input className="input" value={q} onChange={(e) => setQ(e.target.value)} placeholder={t('admin.searchPlaceholder')} /></div>
            </div>

            <table className="table is-fullwidth is-striped is-hoverable">
              <thead>
                <tr>
                  <th>{t('auth.email')}</th>
                  <th>{t('admin.name')}</th>
                  <th>{t('admin.role')}</th>
                  <th>{t('admin.active')}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(u => (
                  <tr key={u.id} style={{ cursor: 'pointer' }} className={u.id === selectedId ? 'is-selected' : ''} onClick={() => setSelectedId(u.id)}>
                    <td>{u.email}</td>
                    <td>{u.first_name} {u.last_name}</td>
                    <td><span className="tag is-light">{u.role}</span></td>
                    <td>{u.is_active ? t('common.yes') : t('common.no')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="column">
          <div className="box">
            <h2 className="title is-6">{t('admin.edit')}</h2>
            {!selected ? (
              <p className="has-text-grey">{t('admin.selectUser')}</p>
            ) : (
              <div>
                <p className="is-size-7 has-text-grey">{selected.email}</p>

                <div className="columns">
                  <div className="column">
                    <div className="field">
                      <label className="label">{t('auth.firstName')}</label>
                      <div className="control"><input className="input" value={eFirst} onChange={(e) => setEFirst(e.target.value)} /></div>
                    </div>
                  </div>
                  <div className="column">
                    <div className="field">
                      <label className="label">{t('auth.lastName')}</label>
                      <div className="control"><input className="input" value={eLast} onChange={(e) => setELast(e.target.value)} /></div>
                    </div>
                  </div>
                </div>

                <div className="columns">
                  <div className="column">
                    <div className="field">
                      <label className="label">{t('admin.role')}</label>
                      <div className="control">
                        <div className="select is-fullwidth">
                          <select value={eRole} onChange={(e) => setERole(e.target.value as any)}>
                            <option value="USER">USER</option>
                            <option value="MODERATOR">MODERATOR</option>
                            <option value="ADMIN">ADMIN</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="column">
                    <div className="field">
                      <label className="label">{t('admin.group')}</label>
                      <div className="control">
                        <div className="select is-fullwidth">
                          <select value={eGroupId} onChange={(e) => setEGroupId(e.target.value)}>
                            <option value="">{t('common.dash')}</option>
                            {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="columns">
                  <div className="column">
                    <label className="checkbox">
                      <input type="checkbox" checked={eActive} onChange={(e) => setEActive(e.target.checked)} /> {t('admin.active')}
                    </label>
                  </div>
                  <div className="column">
                    <label className="checkbox">
                      <input type="checkbox" checked={eVerified} onChange={(e) => setEVerified(e.target.checked)} /> {t('admin.emailVerified')}
                    </label>
                  </div>
                </div>

                <div className="field">
                  <label className="label">{t('admin.newPasswordOptional')}</label>
                  <div className="control"><input className="input" type="password" value={ePassword} onChange={(e) => setEPassword(e.target.value)} /></div>
                </div>

                <div className="field is-grouped is-grouped-right">
                  <div className="control">
                    <button
                      className={`button is-dark ${busy ? 'is-loading' : ''}`}
                      onClick={() => {
                        if (!selected) return
                        setBusy(true)
                        setError(null)
                        const doUpdate = apiFetch(`/users/${selected.id}`, {
                          method: 'PUT',
                          body: JSON.stringify({
                            first_name: eFirst,
                            last_name: eLast,
                            role: eRole,
                            is_active: eActive,
                            email_verified: eVerified,
                            group_id: eGroupId || null,
                          }),
                        })
                        const doPwd = ePassword.trim().length >= 8
                          ? apiFetch(`/users/${selected.id}/password`, { method: 'PUT', body: JSON.stringify({ new_password: ePassword }) })
                          : Promise.resolve(null)

                        void Promise.all([doUpdate, doPwd])
                          .then(() => load())
                          .catch((e: any) => setError(e?.message ?? t('common.error')))
                          .finally(() => setBusy(false))
                      }}
                    >
                      {t('common.save')}
                    </button>
                  </div>
                  <div className="control">
                    <button
                      className={`button is-danger is-light ${busy ? 'is-loading' : ''}`}
                      onClick={() => {
                        if (!selected) return
                        if (!confirm(t('admin.confirmDeleteUser'))) return
                        setBusy(true)
                        setError(null)
                        void apiFetch(`/users/${selected.id}`, { method: 'DELETE' })
                          .then(() => {
                            setSelectedId(null)
                            return load()
                          })
                          .catch((e: any) => setError(e?.message ?? t('common.error')))
                          .finally(() => setBusy(false))
                      }}
                    >
                      {t('common.delete')}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
