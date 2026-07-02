import { prisma } from '../../config/prisma.js'

export const tripRepository = {
  async findTrips(params: {
    companyId?: string | null
    status?: string
    departureDate?: string
    routeId?: string
    skip?: number
    take?: number
  }) {
    return prisma.trip.findMany({
      where: {
        companyId: params.companyId ?? undefined,
        status: params.status,
        routeId: params.routeId,
        departureDate: params.departureDate ? new Date(params.departureDate) : undefined
      },
      include: {
        route: true,
        bus: true,
        driver: true,
        _count: { select: { bookings: true } }
      },
      orderBy: [{ departureDate: 'asc' }, { departureTime: 'asc' }],
      skip: params.skip,
      take: params.take
    })
  },

  async findById(id: string) {
    return prisma.trip.findUnique({
      where: { id },
      include: {
        route: true,
        bus: true,
        driver: true,
        bookings: {
          where: { status: 'CONFIRMED' },
          include: { seat: true },
          orderBy: { createdAt: 'asc' }
        }
      }
    })
  },

  async create(data: {
    companyId: string
    routeId: string
    busId: string
    driverId?: string
    departureDate: Date
    departureTime: string
    arrivalTime: string
    baseFare: number
    notes?: string
    availableSeats: number
  }) {
    return prisma.trip.create({
      data: {
        ...data,
        status: 'SCHEDULED',
        bookedSeats: 0
      }
    })
  },

  async update(id: string, data: Partial<{
    departureDate: Date
    departureTime: string
    arrivalTime: string
    baseFare: number
    status: string
    notes: string
    driverId: string
  }>) {
    return prisma.trip.update({ where: { id }, data })
  },

  async countByStatus(companyId: string, status: string) {
    return prisma.trip.count({ where: { companyId, status } })
  },

  async countToday(companyId: string, date: Date) {
    return prisma.trip.count({ where: { companyId, departureDate: date } })
  }
}