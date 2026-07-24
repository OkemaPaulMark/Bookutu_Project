import { api } from './api'

export type CompanyRecord = {
  id: string
  name: string
  email: string
  phoneNumber: string
  address?: string
  city: string
  state: string
  country?: string
  postalCode?: string
  status: 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'INACTIVE'
  registrationNumber: string
  licenseNumber?: string
  description?: string
  website?: string
  taxId?: string
  commissionRate?: number
  createdAt: string
}

export type PlatformStats = {
  companies: { total: number; active: number; pending: number; suspended: number; inactive: number }
  totalTrips: number
  totalBookings: number
  totalRevenue: number
  monthlyRevenue: { month: string; revenue: number }[]
  recentCompanies: { id: string; name: string; city: string; status: string; createdAt: string }[]
  topCompanies: { id: string; name: string; city: string; status: string; bookings: number; trips: number; buses: number }[]
}

export async function getPlatformStatsRequest() {
  const { data } = await api.get<{ data: PlatformStats }>('/companies/platform/stats')
  return data.data
}

export async function listCompaniesRequest() {
  const { data } = await api.get<{ data: CompanyRecord[] }>('/companies')
  return data.data
}

export async function createCompanyRequest(payload: {
  name: string
  email: string
  phoneNumber: string
  address: string
  city: string
  state: string
  registrationNumber: string
  licenseNumber: string
  description?: string
  website?: string
  country?: string
  postalCode?: string
  taxId?: string
  commissionRate?: number
}) {
  const { data } = await api.post<{ data: CompanyRecord }>('/companies', payload)
  return data.data
}

export async function getCompanyRequest(companyId: string) {
  const { data } = await api.get<{ data: CompanyRecord }>(`/companies/${companyId}`)
  return data.data
}

export async function updateCompanyRequest(
  companyId: string,
  payload: Partial<{
    name: string
    description: string
    email: string
    phoneNumber: string
    website: string
    address: string
    city: string
    state: string
    country: string
    postalCode: string
    taxId: string
    licenseNumber: string
    commissionRate: number
    status: 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'INACTIVE'
  }>
) {
  const { data } = await api.patch<{ data: CompanyRecord }>(`/companies/${companyId}`, payload)
  return data.data
}

export async function deleteCompanyRequest(companyId: string) {
  await api.delete(`/companies/${companyId}`)
}

export async function inviteCompanyAdminRequest(payload: {
  email: string
  companyId: string
  firstName?: string
  lastName?: string
  phoneNumber?: string
}) {
  const { data } = await api.post<{
    message: string
    invite: {
      email: string
      companyId: string
      companyName: string
      expiresAt: string
      deliveryMode: 'preview' | 'smtp'
    }
    setupUrl?: string
  }>('/auth/register/staff', payload)

  return data
}
