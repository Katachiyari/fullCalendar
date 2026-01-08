import { useEffect, useMemo, useState } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import { apiFetch } from '../api'
import { useMe } from '../hooks/useMe'
import { useTranslation } from 'react-i18next'

type LegacyEvent = {
  id: string
  title: string
  start: string
  end?: string | null
  all_day: boolean
  description?: string | null
  color?: string | null
  resources?: string[]
  rrule?: string | null
  group_id?: string | null
  owner_id?: string | null
}

type Group = { id: string; slug: string; name: string }

function colorOrDefault(c?: string | null) {
  return c || '#334155'
}

function toDateInputValue(iso: string | undefined | null) {
  if (!iso) return ''
  // Accept YYYY-MM-DD or ISO datetime.
  if (iso.length === 10) return iso
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  // datetime-local expects no timezone
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function toLocalDateTimeString(d: Date | null | undefined) {
  if (!d) return null
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:00`
}

export default function CalendarPage() {
  const { t } = useTranslation()
  const { me } = useMe()
  const [events, setEvents] = useState<LegacyEvent[]>([])
  const [groups, setGroups] = useState<Group[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const [title, setTitle] = useState('')
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [allDay, setAllDay] = useState(false)
  const [description, setDescription] = useState('')
  const [groupId, setGroupId] = useState('')

  const canPickGroup = me?.role === 'ADMIN' || me?.group?.slug === 'chef_projet'

  const [selectedEventId, setSelectedEventId] = useState<string>('')

  const selectedEvent = useMemo(
    () => events.find(e => e.id === selectedEventId) ?? null,
    [events, selectedEventId]
  )

  const upcoming = useMemo(() => {
    const now = Date.now()
    const list = [...events]
      .map(e => ({ e, t: new Date(e.start).getTime() }))
      .filter(x => !Number.isNaN(x.t) && x.t >= now)
      .sort((a, b) => a.t - b.t)
      .slice(0, 8)
      .map(x => x.e)
    return list
  }, [events])

  useEffect(() => {
    const load = async () => {
      setError(null)
      const [ev, gr] = await Promise.all([
        apiFetch('/events/?limit=500'),
        apiFetch('/groups/'),
      ])
      setEvents(Array.isArray(ev) ? ev : [])
      setGroups(Array.isArray(gr) ? gr : [])
    }
    void load().catch((e: any) => setError(e?.message ?? t('common.error')))
  }, [])

  useEffect(() => {
    if (!selectedEvent) return
    setTitle(selectedEvent.title ?? '')
    setStart(toDateInputValue(selectedEvent.start))
    setEnd(toDateInputValue(selectedEvent.end ?? null))
    setAllDay(!!selectedEvent.all_day)
    setDescription(selectedEvent.description ?? '')
    setGroupId(selectedEvent.group_id ?? '')
  }, [selectedEventId])

  async function reloadEvents() {
    const ev = await apiFetch('/events/?limit=500')
    setEvents(Array.isArray(ev) ? ev : [])
  }

  async function submit() {
    setError(null)
    setBusy(true)
    try {
      const payload: any = {
        title,
        description: description || null,
        start: start || null,
        end: end || null,
        all_day: allDay,
      }
      if (canPickGroup) payload.group_id = groupId || null

      if (!selectedEventId) {
        await apiFetch('/events/', { method: 'POST', body: JSON.stringify(payload) })
      } else {
        await apiFetch(`/events/${selectedEventId}`, { method: 'PUT', body: JSON.stringify(payload) })
      }

      await reloadEvents()
      setSelectedEventId('')
      setTitle('')
      setStart('')
      setEnd('')
      setAllDay(false)
      setDescription('')
      setGroupId('')
    } catch (e: any) {
      setError(e?.message ?? t('common.error'))
    } finally {
      setBusy(false)
    }
  }

  async function deleteSelected() {
    if (!selectedEventId) return
    if (!confirm(t('calendar.confirmDeleteEvent'))) return
    setError(null)
    setBusy(true)
    try {
      await apiFetch(`/events/${selectedEventId}`, { method: 'DELETE' })
      await reloadEvents()
      setSelectedEventId('')
    } catch (e: any) {
      setError(e?.message ?? t('common.error'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="opshub-fade-in animate__animated animate__fadeIn">
      {error && <div className="notification is-danger is-light">{error}</div>}

      <div className="columns">
        <div className="column is-9">
          <div className="box">
            <h2 className="title is-6">{selectedEventId ? t('calendar.editEvent') : t('calendar.createEvent')}</h2>

            <div className="columns">
              <div className="column">
                <div className="field">
                  <label className="label">{t('calendar.title')}</label>
                  <div className="control">
                    <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} />
                  </div>
                </div>
              </div>
              <div className="column is-2">
                <label className="checkbox" style={{ marginTop: '2.25rem', display: 'inline-block' }}>
                  <input type="checkbox" checked={allDay} onChange={(e) => setAllDay(e.target.checked)} /> {t('calendar.allDay')}
                </label>
              </div>
            </div>

            <div className="columns">
              <div className="column">
                <div className="field">
                  <label className="label">{t('calendar.start')}</label>
                  <div className="control">
                    <input className="input" type="datetime-local" value={start} onChange={(e) => setStart(e.target.value)} />
                  </div>
                </div>
              </div>
              <div className="column">
                <div className="field">
                  <label className="label">{t('calendar.end')}</label>
                  <div className="control">
                    <input className="input" type="datetime-local" value={end} onChange={(e) => setEnd(e.target.value)} />
                  </div>
                </div>
              </div>
              <div className="column">
                <div className="field">
                  <label className="label">{t('calendar.group')}</label>
                  <div className="control">
                    <div className="select is-fullwidth">
                      <select value={groupId} onChange={(e) => setGroupId(e.target.value)} disabled={!canPickGroup}>
                        <option value="">—</option>
                        {groups.map(g => (
                          <option key={g.id} value={g.id}>{g.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  {!canPickGroup && <p className="help">{t('calendar.groupRestricted')}</p>}
                </div>
              </div>
            </div>

            <div className="field">
              <label className="label">{t('calendar.description')}</label>
              <div className="control">
                <textarea className="textarea" value={description} onChange={(e) => setDescription(e.target.value)} />
              </div>
            </div>

            <div className="field is-grouped is-grouped-right">
              {selectedEventId && (
                <div className="control">
                  <button className={`button is-danger is-light ${busy ? 'is-loading' : ''}`} onClick={() => void deleteSelected()}>
                    {t('calendar.delete')}
                  </button>
                </div>
              )}
              <div className="control">
                <button
                  className={`button is-dark ${busy ? 'is-loading' : ''}`}
                  disabled={!title.trim() || !start.trim()}
                  onClick={() => void submit()}
                >
                  {selectedEventId ? t('calendar.save') : t('calendar.create')}
                </button>
              </div>
            </div>

            <p className="help">{t('calendar.hint')}</p>
          </div>

          <div className="box">
            <FullCalendar
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
              initialView="dayGridMonth"
              headerToolbar={{ left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek' }}
              editable
              selectable
              events={events.map(e => ({
                id: e.id,
                title: e.title,
                start: e.start,
                end: e.end ?? undefined,
                allDay: e.all_day,
                backgroundColor: colorOrDefault(e.color),
                borderColor: colorOrDefault(e.color),
              }))}
              select={(info) => {
                setSelectedEventId('')
                setTitle('')
                setStart(toDateInputValue(info.start.toISOString()))
                setEnd(toDateInputValue(info.end?.toISOString() ?? null))
                setAllDay(!!info.allDay)
                setDescription('')
              }}
              eventClick={(info) => {
                setSelectedEventId(String(info.event.id))
              }}
              eventDrop={async (info) => {
                try {
                  await apiFetch(`/events/${info.event.id}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                      start: toLocalDateTimeString(info.event.start),
                      end: toLocalDateTimeString(info.event.end),
                      all_day: !!info.event.allDay,
                    }),
                  })
                  await reloadEvents()
                } catch (e: any) {
                  setError(e?.message ?? t('common.error'))
                  info.revert()
                }
              }}
              eventResize={async (info) => {
                try {
                  await apiFetch(`/events/${info.event.id}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                      start: toLocalDateTimeString(info.event.start),
                      end: toLocalDateTimeString(info.event.end),
                      all_day: !!info.event.allDay,
                    }),
                  })
                  await reloadEvents()
                } catch (e: any) {
                  setError(e?.message ?? t('common.error'))
                  info.revert()
                }
              }}
            />
          </div>
        </div>

        <div className="column">
          <div className="box">
            <h3 className="title is-6">{t('calendar.upcoming')}</h3>
            {upcoming.length === 0 ? (
              <p className="has-text-grey">{t('calendar.none')}</p>
            ) : (
              <div>
                {upcoming.map(ev => (
                  <div
                    key={ev.id}
                    className="box is-shadowless"
                    style={{ borderLeft: `4px solid ${colorOrDefault(ev.color)}`, cursor: 'pointer' }}
                    onClick={() => setSelectedEventId(ev.id)}
                  >
                    <p className="is-size-7 has-text-grey">{ev.start}</p>
                    <p className="has-text-weight-semibold">{ev.title}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="box">
            <h3 className="title is-6">{t('calendar.stats')}</h3>
            <div className="content is-small">
              <p><strong>{t('calendar.totalVisible')}:</strong> {events.length}</p>
              <p><strong>{t('calendar.myEvents')}:</strong> {me?.id ? events.filter(e => e.owner_id === me.id).length : '—'}</p>
              <p><strong>{t('calendar.role')}:</strong> {me?.role ?? '—'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
