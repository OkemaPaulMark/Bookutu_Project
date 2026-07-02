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
    page?: number
    limit?: number
  }) {
    const page = input.page ?? 1
    const limit = input.limit ?? 20
    const skip = (page - 1) * limit

    // Passengers see all SCHEDULED trips across all companies
    const companyScope = input.userType === 'SUPER_ADMIN' || input.userType === 'PASSENGER'
      ? undefined
      : input.companyId

    const statusScope = input.userType === 'PASSENGER' ? (input.status ?? 'SCHEDULED') : input.status

    return tripRepository.findTrips({
      companyId: companyScope,
      status: statusScope,
      departureDate: input.departureDate,
      routeId: input.routeId,
      skip,
      take: limit
    })
  },

  async getTrip(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
  }) {
    const trip = await tripRepository.findById(input.id)
    if (!trip) throw new AppError(404, 'Trip not found')

    // Passengers can view any SCHEDULED trip
    if (input.userType === 'PASSENGER') {
      if (trip.status !== 'SCHEDULED') throw new AppError(404, 'Trip not found')
      return trip
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

    const [totalTrips, scheduledTrips, completedTrips, cancelledTrips, todayTrips,
      bookingAgg, confirmedBookings, pendingBookings, cancelledBookings,
      buses, routes, drivers, routeTrips] = await Promise.all([
      prisma.trip.count({ where: { companyId: input.companyId } }),
      tripRepository.countByStatus(input.companyId, 'SCHEDULED'),
      tripRepository.countByStatus(input.companyId, 'COMPLETED'),
      tripRepository.countByStatus(input.companyId, 'CANCELLED'),
      tripRepository.countToday(input.companyId, today),
      // total revenue from confirmed/completed bookings
      prisma.booking.aggregate({
        where: { companyId: input.companyId, status: { in: ['CONFIRMED', 'COMPLETED'] } },
        _sum: { totalAmount: true },
        _count: { id: true }
      }),
      prisma.booking.count({ where: { companyId: input.companyId, status: 'CONFIRMED' } }),
      prisma.booking.count({ where: { companyId: input.companyId, status: 'PENDING' } }),
      prisma.booking.count({ where: { companyId: input.companyId, status: 'CANCELLED' } }),
      // fleet counts
      prisma.bus.groupBy({ by: ['status'], where: { companyId: input.companyId }, _count: { id: true } }),
      prisma.route.count({ where: { companyId: input.companyId, isActive: true } }),
      prisma.driver.count({ where: { companyId: input.companyId, status: 'ACTIVE' } }),
      // route performance: top 5 routes by booking count
      prisma.trip.findMany({
        where: { companyId: input.companyId },
        include: {
          route: { select: { name: true, originCity: true, destinationCity: true } },
          _count: { select: { bookings: true } },
          bookings: { where: { status: { in: ['CONFIRMED', 'COMPLETED'] } }, select: { totalAmount: true } }
        }
      })
    ])

    // Aggregate route performance
    const routeMap = new Map<string, { route: string; trips: number; revenue: number; bookedSeats: number; totalSeats: number }>()
    for (const trip of routeTrips) {
      const key = trip.routeId
      const label = `${trip.route.originCity} → ${trip.route.destinationCity}`
      const rev = trip.bookings.reduce((s: number, b: any) => s + Number(b.totalAmount), 0)
      const existing = routeMap.get(key)
      if (existing) {
        existing.trips += 1
        existing.revenue += rev
        existing.bookedSeats += trip.bookings.length
      } else {
        routeMap.set(key, { route: label, trips: 1, revenue: rev, bookedSeats: trip.bookings.length, totalSeats: 0 })
      }
    }
    const routePerformance = Array.from(routeMap.values())
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 5)

    // Monthly revenue for last 6 months
    const sixMonthsAgo = new Date()
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 5)
    sixMonthsAgo.setDate(1)
    sixMonthsAgo.setHours(0, 0, 0, 0)
    const recentBookings = await prisma.booking.findMany({
      where: {
        companyId: input.companyId,
        status: { in: ['CONFIRMED', 'COMPLETED'] },
        createdAt: { gte: sixMonthsAgo }
      },
      select: { totalAmount: true, createdAt: true }
    })
    const monthlyMap = new Map<string, number>()
    for (const b of recentBookings) {
      const key = b.createdAt.toISOString().slice(0, 7) // YYYY-MM
      monthlyMap.set(key, (monthlyMap.get(key) ?? 0) + Number(b.totalAmount))
    }
    const monthlyRevenue = Array.from(monthlyMap.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, revenue]) => ({ month, revenue }))

    const busStatusMap: Record<string, number> = {}
    for (const g of buses) busStatusMap[g.status] = g._count.id

    return {
      totalTrips,
      scheduledTrips,
      completedTrips,
      cancelledTrips,
      todayTrips,
      totalRevenue: Number(bookingAgg._sum.totalAmount ?? 0),
      totalBookings: bookingAgg._count.id,
      confirmedBookings,
      pendingBookings,
      cancelledBookings,
      fleet: {
        active: busStatusMap['ACTIVE'] ?? 0,
        maintenance: busStatusMap['MAINTENANCE'] ?? 0,
        inactive: busStatusMap['INACTIVE'] ?? 0,
        total: Object.values(busStatusMap).reduce((s, v) => s + v, 0)
      },
      activeRoutes: routes,
      activeDrivers: drivers,
      routePerformance,
      monthlyRevenue
    }
  }
}