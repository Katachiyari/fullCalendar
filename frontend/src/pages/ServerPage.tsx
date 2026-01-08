import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import { useTranslation } from 'react-i18next'

type Metrics = {
  cpu: { cores: number; load: { avg_1: number; avg_5: number; avg_15: number } }
  memory: { total_bytes: number | null; used_bytes: number | null; available_bytes: number | null }
  storage: { path: string; total_bytes: number | null; used_bytes: number | null; free_bytes: number | null }
}

type ServerTarget = { id: string; host: string; name?: string | null; ssh_port: number; disk_path: string }

type RemoteMetrics = Metrics & {
  target: { host: string; ssh_port: number; disk_path: string }
  reachable: boolean
  collected_at: string
  method: string | null
  error: string | null
}

function fmtBytes(v: number | null, dash: string) {
  if (v == null) return dash
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let x = v
  let i = 0
  while (x >= 1024 && i < units.length - 1) {
    x /= 1024
    i++
  }
  return `${x.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

export default function ServerPage() {
  const { t } = useTranslation()
  const [data, setData] = useState<Metrics | null>(null)
  const [targets, setTargets] = useState<ServerTarget[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [remote, setRemote] = useState<RemoteMetrics | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const dash = t('common.dash')

  const [newHost, setNewHost] = useState('')
  const [newName, setNewName] = useState('')

  async function load() {
    setError(null)
    try {
      const resp = await apiFetch('/admin/server-metrics')
      setData(resp)
      const rows = await apiFetch('/admin/servers')
      setTargets(rows)
    } catch (e: any) {
      setError(e?.message ?? t('common.error'))
    }
  }

  async function loadRemote(serverId: string) {
    setError(null)
    setBusy(true)
    try {
      const resp = await apiFetch(`/admin/servers/${serverId}/metrics`)
      setRemote(resp)
    } catch (e: any) {
      setError(e?.message ?? t('common.error'))
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  return (
    <div className="opshub-fade-in animate__animated animate__fadeIn">
      <div className="level">
        <div className="level-left">
          <h1 className="title is-5 mb-0">{t('server.title')}</h1>
        </div>
        <div className="level-right">
          <button className="button is-dark" onClick={() => void load()}>{t('common.refresh')}</button>
        </div>
      </div>

      {error && <div className="notification is-danger is-light">{error}</div>}

      <div className="box">
        <h2 className="title is-6">{t('server.targets')}</h2>

        <div className="columns is-multiline">
          <div className="column is-5">
            <div className="field">
              <label className="label">{t('server.host')}</label>
              <div className="control">
                <input className="input" value={newHost} onChange={(e) => setNewHost(e.target.value)} placeholder="10.0.0.10" />
              </div>
            </div>
          </div>
          <div className="column is-5">
            <div className="field">
              <label className="label">{t('server.nameOptional')}</label>
              <div className="control">
                <input className="input" value={newName} onChange={(e) => setNewName(e.target.value)} placeholder={t('common.optional')} />
              </div>
            </div>
          </div>
          <div className="column is-2" style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              className={`button is-dark is-fullwidth ${busy ? 'is-loading' : ''}`}
              disabled={!newHost.trim()}
              onClick={() => {
                setBusy(true)
                setError(null)
                void apiFetch('/admin/servers', {
                  method: 'POST',
                  body: JSON.stringify({ host: newHost.trim(), name: newName.trim() || null }),
                })
                  .then(() => load())
                  .then(() => {
                    setNewHost('')
                    setNewName('')
                  })
                  .catch((e: any) => setError(e?.message ?? t('common.error')))
                  .finally(() => setBusy(false))
              }}
            >
              {t('server.add')}
            </button>
          </div>
        </div>

        {targets.length === 0 ? (
          <p className="has-text-grey">{t('server.noTargets')}</p>
        ) : (
          <table className="table is-fullwidth is-striped is-hoverable">
            <thead>
              <tr>
                <th>{t('server.host')}</th>
                <th>{t('server.name')}</th>
                <th>{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {targets.map((s) => (
                <tr key={s.id} className={s.id === selectedId ? 'is-selected' : ''}>
                  <td style={{ cursor: 'pointer' }} onClick={() => { setSelectedId(s.id); void loadRemote(s.id) }}>
                    {s.host}
                  </td>
                  <td>{s.name ?? dash}</td>
                  <td>
                    <div className="buttons are-small">
                      <button className={`button is-dark ${busy ? 'is-loading' : ''}`} onClick={() => void loadRemote(s.id)}>
                        {t('common.refresh')}
                      </button>
                      <button
                        className={`button is-danger is-light ${busy ? 'is-loading' : ''}`}
                        onClick={() => {
                          if (!confirm(t('server.confirmDelete'))) return
                          setBusy(true)
                          setError(null)
                          void apiFetch(`/admin/servers/${s.id}`, { method: 'DELETE' })
                            .then(() => {
                              if (selectedId === s.id) {
                                setSelectedId(null)
                                setRemote(null)
                              }
                              return load()
                            })
                            .catch((e: any) => setError(e?.message ?? t('common.error')))
                            .finally(() => setBusy(false))
                        }}
                      >
                        {t('common.delete')}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {selectedId && remote && (
          <div className="notification is-light mt-3">
            <p className="is-size-7">
              <strong>{t('server.status')}:</strong> {remote.reachable ? t('server.reachable') : t('server.unreachable')} ·{' '}
              <strong>{t('server.method')}:</strong> {remote.method ?? dash} ·{' '}
              <strong>{t('server.collectedAt')}:</strong> {new Date(remote.collected_at).toLocaleString()}
            </p>
            {remote.error && <p className="is-size-7 has-text-danger">{remote.error}</p>}
            {!remote.method && (
              <p className="is-size-7 has-text-grey mt-2">{t('server.sshHint')}</p>
            )}
          </div>
        )}
      </div>

      {!data ? (
        <progress className="progress is-small is-dark" max={100}>{t('common.loading')}</progress>
      ) : (
        <div className="columns">
          <div className="column">
            <div className="box">
              <h2 className="title is-6">{t('server.cpu')}</h2>
              <div className="content is-small">
                <p><strong>{t('server.cores')}:</strong> {data.cpu.cores}</p>
                <p><strong>{t('server.load')}:</strong> {data.cpu.load.avg_1.toFixed(2)} / {data.cpu.load.avg_5.toFixed(2)} / {data.cpu.load.avg_15.toFixed(2)}</p>
              </div>
            </div>
          </div>

          <div className="column">
            <div className="box">
              <h2 className="title is-6">{t('server.memory')}</h2>
              <div className="content is-small">
                <p><strong>{t('server.total')}:</strong> {fmtBytes(data.memory.total_bytes, dash)}</p>
                <p><strong>{t('server.used')}:</strong> {fmtBytes(data.memory.used_bytes, dash)}</p>
                <p><strong>{t('server.available')}:</strong> {fmtBytes(data.memory.available_bytes, dash)}</p>
              </div>
            </div>
          </div>

          <div className="column">
            <div className="box">
              <h2 className="title is-6">{t('server.storage')}</h2>
              <div className="content is-small">
                <p><strong>{t('server.path')}:</strong> {data.storage.path}</p>
                <p><strong>{t('server.total')}:</strong> {fmtBytes(data.storage.total_bytes, dash)}</p>
                <p><strong>{t('server.used')}:</strong> {fmtBytes(data.storage.used_bytes, dash)}</p>
                <p><strong>{t('server.free')}:</strong> {fmtBytes(data.storage.free_bytes, dash)}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
