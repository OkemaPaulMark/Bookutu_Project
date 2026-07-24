import { api } from './api'

export type DeliveryStatus = 'REGISTERED' | 'ON_DELIVERY' | 'PICKED_UP' | 'CANCELLED'

export type DeliveryStaffSummary = {
  id: string
  firstName: string
  lastName: string
}

export type DeliveryRecord = {
  id: string
  trackingNumber: string
  companyId: string
  sentAt: string
  senderName: string
  senderPhone: string
  receiverName: string
  receiverPhone: string
  originTerminal: string
  destinationTerminal: string
  packageDescription: string
  fee: number
  status: DeliveryStatus
  registeredBy: DeliveryStaffSummary | null
  pickedUpBy: DeliveryStaffSummary | null
  pickedUpAt?: string | null
  createdAt: string
  updatedAt: string
}

export async function listDeliveriesRequest(params?: { status?: DeliveryStatus; search?: string }) {
  const { data } = await api.get<{ data: DeliveryRecord[] }>('/deliveries', { params })
  return data.data
}

export async function createDeliveryRequest(payload: {
  sentAt: string
  senderName: string
  senderPhone: string
  receiverName: string
  receiverPhone: string
  originTerminal: string
  destinationTerminal: string
  packageDescription: string
  fee: number
}) {
  const { data } = await api.post<{ data: DeliveryRecord }>('/deliveries', payload)
  return data.data
}

export async function updateDeliveryStatusRequest(id: string, status: DeliveryStatus) {
  const { data } = await api.patch<{ data: DeliveryRecord }>(`/deliveries/${id}/status`, { status })
  return data.data
}

export async function deleteDeliveryRequest(id: string) {
  await api.delete(`/deliveries/${id}`)
}
