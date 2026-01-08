import { useState } from 'react'
import { apiFetch } from '../api'
import { useTranslation } from 'react-i18next'

type Host = { name: string; ip: string | null }
type Group = { group: string; hosts: Host[] }

type AnalyzeResponse = {
  inventory_file: string
  groups: Group[]
}

export default function AnsiblePage() {
  const { t } = useTranslation()
  const [path, setPath] = useState('')
  const [data, setData] = useState<AnalyzeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function analyze() {
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const resp = await apiFetch('/ansible/analyze', {
        method: 'POST',
        body: JSON.stringify({ path }),
      })
      setData(resp)
    } catch (e: any) {
      setError(e?.message ?? t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="opshub-fade-in animate__animated animate__fadeIn">
      <div className="level">
        <div className="level-left">
          <h1 className="title is-5 mb-0">{t('ansible.title')}</h1>
        </div>
      </div>

      <div className="content">
        <p className="help">{t('ansible.howItWorks')}</p>
      </div>

      <div className="box">
        <div className="field">
          <label className="label">{t('ansible.inventoryPath')}</label>
          <div className="control">
            <input className="input" value={path} onChange={(e) => setPath(e.target.value)} placeholder={t('ansible.inventoryPlaceholder')} />
          </div>
          <p className="help">{t('ansible.inventoryHelp')}</p>
        </div>

        <div className="field is-grouped is-grouped-right">
          <div className="control">
            <button className={`button is-dark ${loading ? 'is-loading' : ''}`} onClick={() => void analyze()} disabled={!path.trim()}>
              {t('ansible.analyze')}
            </button>
          </div>
        </div>

        {error && <div className="notification is-danger is-light">{error}</div>}

        {data && (
          <div className="content">
            <p><strong>{t('ansible.inventory')}:</strong> {data.inventory_file}</p>
            {data.groups.map((g) => (
              <div key={g.group} className="box">
                <h2 className="title is-6">{g.group}</h2>
                {g.hosts.length === 0 ? (
                  <p className="has-text-grey">{t('ansible.noHosts')}</p>
                ) : (
                  <table className="table is-fullwidth is-striped is-hoverable">
                    <thead>
                      <tr>
                        <th>{t('ansible.name')}</th>
                        <th>{t('common.ip')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {g.hosts.map((h) => (
                        <tr key={`${g.group}-${h.name}`}>
                          <td>{h.name}</td>
                          <td>{h.ip ?? t('common.dash')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
