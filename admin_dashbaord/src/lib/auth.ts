import { api } from './api'

export type AuthApiUser = {
  id: string
  email: string
  username?: string | null
  firstName?: string | null
  lastName?: string | null
  phoneNumber?: string | null
  userType: 'SUPER_ADMIN' | 'COMPANY_STAFF' | 'PASSENGER'
  companyId?: string | null
  companyName?: string | null
  companyStatus?: 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'INACTIVE' | null
  isVerified: boolean
  createdAt?: string
}

export type AuthResponse = {
  access: string
  refresh: string
  user: AuthApiUser
}

export type PasswordSetupDetails = {
  email: string
  firstName?: string | null
  lastName?: string | null
  phoneNumber?: string | null
  companyName?: string | null
}

export async function loginRequest(payload: { email: string, password: string }) {
  const { data } = await api.post<AuthResponse>('/auth/login', payload)
  return data
}

export async function meRequest(accessToken?: string) {
  const { data } = await api.get<{ user: AuthApiUser }>('/auth/me', {
    headers: accessToken
      ? {
          Authorization: `Bearer ${accessToken}`
        }
      : undefined
  })
  return data.user
}

export async function refreshRequest(refresh: string) {
  const { data } = await api.post<{ access: string, refresh: string }>('/auth/refresh', { refresh })
  return data
}

export async function fetchPasswordSetupDetails(token: string) {
  const { data } = await api.get<PasswordSetupDetails>(`/auth/password-setup/${token}`)
  return data
}

export async function setPasswordRequest(payload: {
  token: string
  firstName: string
  lastName: string
  phoneNumber?: string
  password: string
  confirmPassword: string
}) {
  const { data } = await api.post<AuthResponse>('/auth/set-password', payload)
  return data
}
