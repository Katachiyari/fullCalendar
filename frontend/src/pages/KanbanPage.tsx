import { useEffect, useMemo, useState } from 'react'
import { useAutoAnimate } from '@formkit/auto-animate/react'
import { apiFetch } from '../api'
import { useTranslation } from 'react-i18next'

type Task = {
  id: string
  title: string
  status: 'TODO'|'IN_PROGRESS'|'DONE'
  priority: 'P0'|'P1'|'P2'|'P3'
  estimate_hours?: number | null
  gitlab_mr_url?: string | null
  gitlab_job_url?: string | null
}

function priClass(p: Task['priority']) {
  if (p === 'P0') return 'is-danger'
  if (p === 'P1') return 'is-warning'
  if (p === 'P2') return 'is-info'
  return 'is-success'
}

function KanbanColumn(props: {
  col: Task['status']
  tasks: Task[]
  moveTask: (taskId: string, status: Task['status']) => void
}) {
  const { t: tr } = useTranslation()
  const [parent] = useAutoAnimate()

  const { col, tasks, moveTask } = props

  return (
    <div className="column">
      <div className="box">
        <div className="mb-3">
          <span className="tag is-light">
            {col === 'TODO' ? tr('kanban.todo') : col === 'IN_PROGRESS' ? tr('kanban.inProgress') : tr('kanban.done')}
          </span>
        </div>

        {tasks.length === 0 && <p className="has-text-grey">{tr('kanban.empty')}</p>}

        <div ref={parent}>
          {tasks.map(task => (
            <article key={task.id} className="message is-light mb-3">
              <div className="message-header">
                <p style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{task.title}</p>
                <span className={`tag ${priClass(task.priority)}`}>{task.priority}</span>
              </div>
              <div className="message-body">
                <div className="is-size-7 has-text-grey mb-2">
                  {task.estimate_hours != null && <span>{tr('kanban.estimate')}: {task.estimate_hours}h</span>}
                  {task.estimate_hours != null && (task.gitlab_mr_url || task.gitlab_job_url) && <span> · </span>}
                  {task.gitlab_mr_url && <a href={task.gitlab_mr_url} target="_blank" rel="noreferrer">{tr('kanban.gitlabMr')}</a>}
                  {task.gitlab_mr_url && task.gitlab_job_url && <span> · </span>}
                  {task.gitlab_job_url && <a href={task.gitlab_job_url} target="_blank" rel="noreferrer">{tr('kanban.gitlabJob')}</a>}
                </div>

                <div className="buttons are-small">
                  {task.status !== 'TODO' && <button className="button" onClick={() => moveTask(task.id, 'TODO')}>{tr('kanban.todo')}</button>}
                  {task.status !== 'IN_PROGRESS' && <button className="button" onClick={() => moveTask(task.id, 'IN_PROGRESS')}>{tr('kanban.inProgress')}</button>}
                  {task.status !== 'DONE' && <button className="button" onClick={() => moveTask(task.id, 'DONE')}>{tr('kanban.done')}</button>}
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function KanbanPage() {
  const { t: tr } = useTranslation()
  const [tasks, setTasks] = useState<Task[]>([])
  const [error, setError] = useState<string | null>(null)

  const columns = useMemo(() => {
    const by: Record<string, Task[]> = { TODO: [], IN_PROGRESS: [], DONE: [] }
    for (const t of tasks) by[t.status].push(t)
    return by
  }, [tasks])

  async function load() {
    setError(null)
    try {
      const data = await apiFetch('/v2/tasks?limit=200')
      setTasks(data)
    } catch (e: any) {
      setError(e?.message ?? tr('common.error'))
    }
  }

  useEffect(() => { void load() }, [])

  async function moveTask(taskId: string, status: Task['status']) {
    setError(null)
    try {
      await apiFetch(`/v2/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify({ status }) })
      await load()
    } catch (e: any) {
      setError(e?.message ?? tr('common.error'))
    }
  }

  return (
    <div className="opshub-fade-in animate__animated animate__fadeIn">
      <div className="level">
        <div className="level-left">
          <h1 className="title is-5 mb-0">{tr('kanban.title')}</h1>
        </div>
        <div className="level-right">
          <button className="button is-dark" onClick={() => void load()}>{tr('common.refresh')}</button>
        </div>
      </div>

      {error && <div className="notification is-danger is-light">{error}</div>}

      <div className="columns">
        {(['TODO', 'IN_PROGRESS', 'DONE'] as const).map(col => (
          <KanbanColumn
            key={col}
            col={col}
            tasks={columns[col]}
            moveTask={(taskId, status) => void moveTask(taskId, status)}
          />
        ))}
      </div>

      <p className="help">
        {tr('kanban.note')}
      </p>
    </div>
  )
}
