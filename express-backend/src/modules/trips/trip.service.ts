import { tripRepository } from './trip.repository.js'
import { AppError } from '../../utils/AppError.js'
import { prisma } from '../../config/prisma.js'

export const tripService = {
  async listTrips(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
    status?: string
    departureDate?: string
    routeId?: string
  }) {
    const companyScope = input.userType === 'SUPER_ADMIN' ? undefined : input.companyId
    return tripRepository.findTrips({
      companyId: companyScope,
      status: input.status,
      departureDate: input.departureDate,
      routeId: input.routeId
    })
  },

  async getTrip(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
  }) {
    const trip = await tripRepository.findById(input.id)
    if (!trip) {
      throw new AppError(404, 'Trip not found')
    }

    if (input.userType !== 'SUPER_ADMIN' && trip.companyId !== input.companyId) {
      throw new AppError(403, 'Insufficient permissions')
    }

    return trip
  },

  async createTrip(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
    body: {
      companyId?: string
      routeId: string
      busId: string
      driverId?: string
      departureDate: string
      departureTime: string
      arrivalTime: string
      baseFare: number
      notes?: string
    }
  }) {
    const companyId = input.userType === 'SUPER_ADMIN' ? input.body.companyId : input.companyId
    if (!companyId) {
      throw new AppError(400, 'companyId is required')
    }

    const bus = await prisma.bus.findUnique({ where: { id: input.body.busId } })
    if (!bus || bus.companyId !== companyId) {
      throw new AppError(400, 'Invalid bus for company')
    }

    const route = await prisma.route.findUnique({ where: { id: input.body.routeId } })
    if (!route || route.companyId !== companyId) {
      throw new AppError(400, 'Invalid route for company')
    }

    return tripRepository.create({
      companyId,
      routeId: input.body.routeId,
      busId: input.body.busId,
      driverId: input.body.driverId,
      departureDate: new Date(input.body.departureDate),
      departureTime: input.body.departureTime,
      arrivalTime: input.body.arrivalTime,
      baseFare: input.body.baseFare,
      notes: input.body.notes,
      availableSeats: bus.totalSeats
    })
  },

  async updateTrip(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
    body: Partial<{
      departureDate: string
      departureTime: string
      arrivalTime: string
      baseFare: number
      status: string
      notes: string
      driverId: string
    }>
  }) {
    await this.getTrip({ id: input.id, userType: input.userType, companyId: input.companyId })

    return tripRepository.update(input.id, {
      ...input.body,
      departureDate: input.body.departureDate ? new Date(input.body.departureDate) : undefined
    })
  },

  async manifest(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
  }) {
    const trip = await this.getTrip(input)
    const totalRevenue = trip.bookings.reduce((sum: number, b: any) => sum + Number(b.totalAmount), 0)

    return {
      tripId: trip.id,
      tripDetails: {
        route: `${trip.route.originCity} -> ${trip.route.destinationCity}`,
        departureDate: trip.departureDate,
        departureTime: trip.departureTime,
        bus: trip.bus.licensePlate
      },
      passengers: trip.bookings.map((booking: any) => ({
        bookingReference: booking.bookingReference,
        passengerName: booking.passengerName,
        passengerPhone: booking.passengerPhone,
        seatNumber: booking.seat.seatNumber,
        amountPaid: booking.totalAmount
      })),
      totalPassengers: trip.bookings.length,
      totalRevenue
    }
  },

  async dashboardStats(input: { companyId: string }) {
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    const [totalTrips, scheduledTrips, completedTrips, cancelledTrips, todayTrips] = await Promise.all([
      prisma.trip.count({ where: { companyId: input.companyId } }),
      tripRepository.countByStatus(input.companyId, 'SCHEDULED'),
      tripRepository.countByStatus(input.companyId, 'COMPLETED'),
      tripRepository.countByStatus(input.companyId, 'CANCELLED'),
      tripRepository.countToday(input.companyId, today)
    ])

    return {
      totalTrips,
      scheduledTrips,
      completedTrips,
      cancelledTrips,
      todayTrips
    }
  }
}