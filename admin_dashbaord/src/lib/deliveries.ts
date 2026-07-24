import { api } from './api'

export type DeliveryStatus = 'REGISTERED' | 'PICKED_UP' | 'CANCELLED'

export type DeliveryStaffSummary = {
  id: string
  firstName: string
  lastName: string
}

export type DeliveryRecord = {
  id: string
  trackingNumber: string
  companyId: string
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

export async function pickupDeliveryRequest(id: string) {
  const { data } = await api.patch<{ data: DeliveryRecord }>(`/deliveries/${id}/pickup`)
  return data.data
}

export async function cancelDeliveryRequest(id: string) {
  const { data } = await api.patch<{ data: DeliveryRecord }>(`/deliveries/${id}/cancel`)
  return data.data
}
