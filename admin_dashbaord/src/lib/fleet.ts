import { api } from './api'

export type BusRecord = {
  id: string
  companyId: string
  licensePlate: string
  model: string
  make: string
  year: number
  totalSeats: number
  busType: string
  hasEntertainment: boolean
  hasRestroom: boolean
  status: 'ACTIVE' | 'MAINTENANCE' | 'INACTIVE'
  imageUrl?: string | null
  createdAt: string
  seats?: SeatRecord[]
  _count?: { seats: number; trips: number }
}

export type SeatRecord = {
  id: string
  busId: string
  seatNumber: string
  rowNumber: number
  seatPosition: string
  seatType: string
  isWindow: boolean
  isAisle: boolean
}

export type RouteRecord = {
  id: string
  companyId: string
  name: string
  originCity: string
  originTerminal: string
  destinationCity: string
  destinationTerminal: string
  distanceKm: number
  estimatedDurationHours: number
  baseFare: number
  isActive: boolean
  createdAt: string
}

export type DriverRecord = {
  id: string
  companyId: string
  firstName: string
  lastName: string
  phoneNumber: string
  email?: string | null
  licenseNumber: string
  licenseExpiryDate: string
  dateOfBirth: string
  employeeId?: string | null
  hireDate: string
  status: string
  createdAt: string
}

// Buses
export async function listBusesRequest() {
  const { data } = await api.get<{ data: BusRecord[] }>('/fleet/buses')
  return data.data
}

export async function getBusRequest(id: string) {
  const { data } = await api.get<{ data: BusRecord }>(`/fleet/buses/${id}`)
  return data.data
}

export async function createBusRequest(payload: {
  licensePlate: string
  model: string
  make: string
  year: number
  totalSeats: number
  busType: string
  hasEntertainment?: boolean
  hasRestroom?: boolean
}) {
  const { data } = await api.post<{ data: BusRecord }>('/fleet/buses', payload)
  return data.data
}

export async function updateBusRequest(id: string, payload: Partial<{
  licensePlate: string
  model: string
  make: string
  year: number
  totalSeats: number
  busType: string
  status: 'ACTIVE' | 'MAINTENANCE' | 'INACTIVE'
  hasEntertainment: boolean
  hasRestroom: boolean
}>) {
  const { data } = await api.patch<{ data: BusRecord }>(`/fleet/buses/${id}`, payload)
  return data.data
}

export async function deleteBusRequest(id: string) {
  await api.delete(`/fleet/buses/${id}`)
}

// Routes
export async function listRoutesRequest() {
  const { data } = await api.get<{ data: RouteRecord[] }>('/fleet/routes')
  return data.data
}

export async function createRouteRequest(payload: {
  name: string
  originCity: string
  originTerminal: string
  destinationCity: string
  destinationTerminal: string
  distanceKm: number
  estimatedDurationHours: number
  baseFare: number
}) {
  const { data } = await api.post<{ data: RouteRecord }>('/fleet/routes', payload)
  return data.data
}

export async function updateRouteRequest(id: string, payload: Partial<{
  name: string
  isActive: boolean
  baseFare: number
}>) {
  const { data } = await api.patch<{ data: RouteRecord }>(`/fleet/routes/${id}`, payload)
  return data.data
}

// Drivers
export async function listDriversRequest() {
  const { data } = await api.get<{ data: DriverRecord[] }>('/fleet/drivers')
  return data.data
}

export async function createDriverRequest(payload: {
  firstName: string
  lastName: string
  phoneNumber: string
  email?: string
  licenseNumber: string
  licenseExpiryDate: string
  dateOfBirth: string
  hireDate: string
  employeeId?: string
}) {
  const { data } = await api.post<{ data: DriverRecord }>('/fleet/drivers', payload)
  return data.data
}

export async function updateDriverRequest(id: string, payload: Partial<{
  firstName: string
  lastName: string
  phoneNumber: string
  email: string
  licenseNumber: string
  licenseExpiryDate: string
  dateOfBirth: string
  hireDate: string
  employeeId: string
  status: string
}>) {
  const { data } = await api.patch<{ data: DriverRecord }>(`/fleet/drivers/${id}`, payload)
  return data.data
}

export async function deleteDriverRequest(id: string) {
  await api.delete(`/fleet/drivers/${id}`)
}
