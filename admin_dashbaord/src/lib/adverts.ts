import { api } from './api'

export type AdvertRecord = {
  id: string
  title: string
  description: string
  imageUrl: string
  linkUrl?: string | null
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export type AdvertPayload = {
  title: string
  description: string
  imageUrl: string
  linkUrl?: string
  isActive?: boolean
}

export async function listAdvertsRequest() {
  const { data } = await api.get<{ data: AdvertRecord[] }>('/adverts')
  return data.data
}

export async function createAdvertRequest(payload: AdvertPayload) {
  const { data } = await api.post<{ data: AdvertRecord }>('/adverts', payload)
  return data.data
}

export async function updateAdvertRequest(advertId: string, payload: Partial<AdvertPayload>) {
  const { data } = await api.patch<{ data: AdvertRecord }>(`/adverts/${advertId}`, payload)
  return data.data
}

export async function deleteAdvertRequest(advertId: string) {
  await api.delete(`/adverts/${advertId}`)
}
