import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import { useTranslation } from 'react-i18next'

type Alert = { id: string; title: string; severity: 'P0'|'P1'|'P2'|'P3'; status: 'OPEN'|'RESOLVED'; created_at: string }
type Task = { id: string; title: string; priority: 'P0'|'P1'|'P2'|'P3'; status: 'TODO'|'IN_PROGRESS'|'DONE'; due_at?: string | null }

function pillColor(p: string) {
  if (p === 'P0') return 'is-danger'
  if (p === 'P1') return 'is-warning'
  if (p === 'P2') return 'is-info'
  return 'is-success'
}

export default function DashboardPage() {
  const { t } = useTranslation()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [tasksToday, setTasksToday] = useState<Task[]>([])
  const [pipeline, setPipeline] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        setError(null)
        const [a, t, p] = await Promise.all([
          apiFetch('/v2/tickets?limit=5'),
          apiFetch('/v2/tasks/today?limit=8'),
          apiFetch('/v2/pipeline/status'),
        ])
        if (!alive) return
        setAlerts(a)
        setTasksToday(t)
        setPipeline(p)
      } catch (e: any) {
        if (!alive) return
        setError(e?.message ?? t('dashboard.loadError'))
      }
    }
    void load()
    const id = window.setInterval(load, 5000)
    return () => { alive = false; window.clearInterval(id) }
  }, [])

  return (
    <div className="opshub-fade-in animate__animated animate__fadeIn">
      <div className="columns is-multiline">
        {error && (
          <div className="column is-12">
            <div className="notification is-danger is-light">{error}</div>
          </div>
        )}
        <div className="column is-6">
          <div className="box">
            <h2 className="title is-6">{t('dashboard.tickets')}</h2>
            {alerts.length === 0 ? (
              <p className="has-text-grey">{t('dashboard.noTickets')}</p>
            ) : (
              <div className="content">
                {alerts.map(a => (
                  <div key={a.id} className="level mb-2">
                    <div className="level-left" style={{ minWidth: 0 }}>
                      <div>
                        <div className="has-text-weight-semibold" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 420 }}>
                          {a.title}
                        </div>
                        <div className="is-size-7 has-text-grey">{new Date(a.created_at).toLocaleString()}</div>
                      </div>
                    </div>
                    <div className="level-right">
                      <span className={`tag ${pillColor(a.severity)}`}>{a.severity}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="column is-6">
          <div className="box">
            <h2 className="title is-6">{t('dashboard.tasksToday')}</h2>
            {tasksToday.length === 0 ? (
              <p className="has-text-grey">{t('dashboard.noTasksToday')}</p>
            ) : (
              <div className="content">
                {tasksToday.map(t => (
                  <div key={t.id} className="level mb-2">
                    <div className="level-left" style={{ minWidth: 0 }}>
                      <div>
                        <div className="has-text-weight-semibold" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 420 }}>
                          {t.title}
                        </div>
                        <div className="is-size-7 has-text-grey">{t.status}</div>
                      </div>
                    </div>
                    <div className="level-right">
                      <span className={`tag ${pillColor(t.priority)}`}>{t.priority}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="column is-12">
          <div className="box">
            <h2 className="title is-6">{t('dashboard.pipelineStatus')}</h2>
            <pre className="has-background-black has-text-white p-3" style={{ borderRadius: 6, overflowX: 'auto' }}>
              {JSON.stringify(pipeline ?? { status: 'unknown' }, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}
