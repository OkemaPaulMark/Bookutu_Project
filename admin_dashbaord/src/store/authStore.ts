import { create } from 'zustand'
import type { AuthUser, UserRole } from '@app-types/auth'

type AuthState = {
  user: AuthUser | null
  loginAs: (role: UserRole) => void
  logout: () => void
}

const AUTH_KEY = 'bookutu_hybrid_auth'

function loadUser(): AuthUser | null {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem(AUTH_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthUser
  } catch {
    return null
  }
}

function saveUser(user: AuthUser | null) {
  if (typeof window === 'undefined') return
  if (!user) {
    localStorage.removeItem(AUTH_KEY)
    return
  }
  localStorage.setItem(AUTH_KEY, JSON.stringify(user))
}

export const useAuthStore = create<AuthState>((set) => ({
  user: loadUser(),
  loginAs: (role) => {
    const user: AuthUser =
      role === 'SUPER_ADMIN'
        ? { name: 'Super Admin', email: 'admin@bookutu.com', role }
        : { name: 'Company Staff', email: 'operator@bookutu.com', role }
    saveUser(user)
    set({ user })
  },
  logout: () => {
    saveUser(null)
    set({ user: null })
  }
}))
