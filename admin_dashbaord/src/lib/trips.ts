import { api } from './api'

export type TripRecord = {
  id: string
  companyId: string
  routeId: string
  busId: string
  driverId?: string | null
  departureDate: string
  departureTime: string
  arrivalTime: string
  baseFare: number
  status: string
  availableSeats: number
  bookedSeats: number
  notes?: string | null
  createdAt: string
  route: { id: string; name: string; originCity: string; destinationCity: string }
  bus: { id: string; licensePlate: string; model: string }
  driver?: { id: string; firstName: string; lastName: string } | null
  _count?: { bookings: number }
}

export type TripStats = {
  totalTrips: number
  scheduledTrips: number
  completedTrips: number
  cancelledTrips: number
  todayTrips: number
  totalRevenue: number
  totalBookings: number
  confirmedBookings: number
  pendingBookings: number
  cancelledBookings: number
  fleet: { active: number; maintenance: number; inactive: number; total: number }
  activeRoutes: number
  activeDrivers: number
  routePerformance: { route: string; trips: number; revenue: number; bookedSeats: number }[]
  monthlyRevenue: { month: string; revenue: number }[]
}

export async function listTripsRequest(params?: { status?: string; departureDate?: string; page?: number; limit?: number }) {
  const { data } = await api.get<{ data: TripRecord[] }>('/trips', { params })
  return data.data
}

export async function createTripRequest(payload: {
  routeId: string
  busId: string
  driverId?: string
  departureDate: string
  departureTime: string
  arrivalTime: string
  baseFare: number
  notes?: string
}) {
  const { data } = await api.post<{ data: TripRecord }>('/trips', payload)
  return data.data
}

export async function updateTripRequest(id: string, payload: Partial<{
  status: string
  routeId: string
  busId: string
  departureDate: string
  departureTime: string
  arrivalTime: string
  baseFare: number
  notes: string
  driverId: string
}>) {
  const { data } = await api.patch<{ data: TripRecord }>(`/trips/${id}`, payload)
  return data.data
}

export async function deleteTripRequest(id: string) {
  await api.delete(`/trips/${id}`)
}

export async function getTripStatsRequest() {
  const { data } = await api.get<{ data: TripStats }>('/trips/dashboard/stats')
  return data.data
}
