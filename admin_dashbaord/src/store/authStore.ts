import { create } from 'zustand'
import type { AuthUser } from '@app-types/auth'
import type { AuthApiUser } from '@/lib/auth'
import { loginRequest, meRequest, refreshRequest, setPasswordRequest } from '@/lib/auth'
import { loadStoredSession, saveStoredSession } from '@/lib/authSession'

type AuthState = {
  accessToken: string | null
  refreshToken: string | null
  user: AuthUser | null
  isHydrating: boolean
  login: (payload: { email: string, password: string }) => Promise<AuthUser>
  restoreSession: () => Promise<void>
  completePasswordSetup: (payload: {
    token: string
    firstName: string
    lastName: string
    phoneNumber?: string
    password: string
    confirmPassword: string
  }) => Promise<AuthUser>
  logout: () => void
}

function mapAuthUser(user: AuthApiUser): AuthUser {
  if (user.userType === 'PASSENGER') {
    throw new Error('Passenger accounts are not allowed in the dashboard.')
  }

  const name = [user.firstName, user.lastName].filter(Boolean).join(' ').trim() || user.email

  return {
    id: user.id,
    name,
    email: user.email,
    role: user.userType,
    firstName: user.firstName,
    lastName: user.lastName,
    phoneNumber: user.phoneNumber,
    companyId: user.companyId ?? null,
    companyName: user.companyName ?? null,
    companyStatus: user.companyStatus ?? null,
    isVerified: user.isVerified
  }
}

function persistSession(accessToken: string, refreshToken: string, user: AuthUser) {
  saveStoredSession({
    accessToken,
    refreshToken,
    user
  })
}

const storedSession = loadStoredSession()

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: storedSession?.accessToken ?? null,
  refreshToken: storedSession?.refreshToken ?? null,
  user: storedSession?.user ?? null,
  isHydrating: false,

  async login(payload) {
    const session = await loginRequest(payload)
    if (session.user.userType === 'PASSENGER') {
      throw new Error('Passenger accounts use the mobile app, not the dashboard.')
    }

    const user = mapAuthUser(session.user)
    persistSession(session.access, session.refresh, user)
    set({
      accessToken: session.access,
      refreshToken: session.refresh,
      user
    })

    return user
  },

  async restoreSession() {
    const currentRefreshToken = get().refreshToken
    const currentAccessToken = get().accessToken

    if (!currentRefreshToken || !currentAccessToken) {
      return
    }

    set({ isHydrating: true })

    try {
      const me = await meRequest()
      const user = mapAuthUser(me)
      persistSession(currentAccessToken, currentRefreshToken, user)
      set({ user, isHydrating: false })
      return
    } catch {
      try {
        const refreshed = await refreshRequest(currentRefreshToken)
        const me = await meRequest(refreshed.access)
        const user = mapAuthUser(me)
        persistSession(refreshed.access, refreshed.refresh, user)
        set({
          accessToken: refreshed.access,
          refreshToken: refreshed.refresh,
          user,
          isHydrating: false
        })
        return
      } catch {
        saveStoredSession(null)
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          isHydrating: false
        })
      }
    }
  },

  async completePasswordSetup(payload) {
    const session = await setPasswordRequest(payload)
    const user = mapAuthUser(session.user)
    persistSession(session.access, session.refresh, user)
    set({
      accessToken: session.access,
      refreshToken: session.refresh,
      user
    })

    return user
  },

  logout() {
    saveStoredSession(null)
    set({
      accessToken: null,
      refreshToken: null,
      user: null
    })
  }
}))
