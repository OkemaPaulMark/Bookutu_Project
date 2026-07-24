import { api } from './api'
import type { AuthApiUser } from './auth'

export async function listUsersRequest(params?: { userType?: string }) {
  const { data } = await api.get<{ data: AuthApiUser[] }>('/auth/users', { params })
  return data.data
}

export async function updateUserRequest(
  userId: string,
  payload: Partial<{
    firstName: string
    lastName: string
    phoneNumber: string
    email: string
    isActive: boolean
    isVerified: boolean
  }>
) {
  const { data } = await api.patch<{ data: AuthApiUser }>(`/auth/${userId}`, payload)
  return data.data
}

export async function deleteUserRequest(userId: string) {
  await api.delete(`/auth/${userId}`)
}
