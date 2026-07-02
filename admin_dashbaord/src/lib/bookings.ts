import { api } from './api'

export type BookingRecord = {
  id: string
  bookingReference: string
  companyId: string
  tripId: string
  passengerId: string
  seatId: string
  status: 'PENDING' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW'
  source: string
  passengerName: string
  passengerPhone: string
  passengerEmail?: string | null
  baseFare: number
  seatFee: number
  serviceFee: number
  totalAmount: number
  createdAt: string
  confirmedAt?: string | null
  cancelledAt?: string | null
  trip: {
    id: string
    departureDate: string
    departureTime: string
    route: { originCity: string; destinationCity: string }
    bus: { licensePlate: string }
  }
  seat: { seatNumber: string }
  passenger: { id: string; email: string; firstName?: string | null; lastName?: string | null }
  payments?: { id: string; status: string; paymentMethod: string; amount: number }[]
}

export async function listBookingsRequest(params?: {
  status?: string
  search?: string
  page?: number
  limit?: number
}) {
  const { data } = await api.get<{ data: BookingRecord[] }>('/bookings', { params })
  return data.data
}

export async function cancelBookingRequest(id: string) {
  const { data } = await api.patch<{ data: BookingRecord }>(`/bookings/${id}/cancel`)
  return data.data
}
