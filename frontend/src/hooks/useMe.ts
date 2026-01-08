import { useEffect, useState } from 'react'
import { apiFetch, getToken } from '../api'
import i18n from '../i18n'

export type Me = {
  id: string
  email: string
  first_name: string
  last_name: string
  phone_number?: string | null
  age?: number | null
  job_title?: string | null
  role: string
  is_active: boolean
  email_verified: boolean
  theme: string
  group_id?: string | null
  group?: { id: string; slug: string; name: string } | null
}

export function useMe() {
  const [me, setMe] = useState<Me | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    const token = getToken()
    if (!token) {
      setMe(null)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const data = await apiFetch('/auth/me')
      setMe(data)
    } catch (e: any) {
      setError(e?.message ?? i18n.t('common.error'))
      setMe(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    // token changes are handled by callers triggering navigation; keep simple
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return { me, loading, error, reload: load }
}
