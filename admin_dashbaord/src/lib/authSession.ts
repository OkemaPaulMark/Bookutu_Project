import type { AuthUser } from '@app-types/auth'

export type StoredSession = {
  accessToken: string
  refreshToken: string
  user: AuthUser
}

const AUTH_KEY = 'bookutu_dashboard_auth'

export function loadStoredSession(): StoredSession | null {
  if (typeof window === 'undefined') return null

  const raw = localStorage.getItem(AUTH_KEY)
  if (!raw) return null

  try {
    return JSON.parse(raw) as StoredSession
  } catch {
    return null
  }
}

export function saveStoredSession(session: StoredSession | null) {
  if (typeof window === 'undefined') return

  if (!session) {
    localStorage.removeItem(AUTH_KEY)
    return
  }

  localStorage.setItem(AUTH_KEY, JSON.stringify(session))
}
