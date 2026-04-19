import { prisma } from '../../config/prisma.js'

export const bookingRepository = {
  async findBookings(params: {
    companyId?: string | null
    status?: 'PENDING' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW'
    search?: string
  }) {
    return prisma.booking.findMany({
      where: {
        companyId: params.companyId ?? undefined,
        status: params.status,
        OR: params.search
          ? [
              { bookingReference: { contains: params.search, mode: 'insensitive' } },
              { passengerName: { contains: params.search, mode: 'insensitive' } },
              { passengerPhone: { contains: params.search, mode: 'insensitive' } }
            ]
          : undefined
      },
      include: {
        trip: { include: { route: true, bus: true } },
        seat: true,
        passenger: { select: { id: true, email: true, firstName: true, lastName: true } }
      },
      orderBy: { createdAt: 'desc' }
    })
  },

  async findById(id: string) {
    return prisma.booking.findUnique({
      where: { id },
      include: {
        trip: { include: { route: true, bus: true } },
        seat: true,
        passenger: { select: { id: true, email: true, firstName: true, lastName: true } },
        payments: true
      }
    })
  },

  async seatIsBooked(tripId: string, seatId: string) {
    const existing = await prisma.booking.findFirst({
      where: {
        tripId,
        seatId,
        status: { in: ['PENDING', 'CONFIRMED'] }
      },
      select: { id: true }
    })
    return Boolean(existing)
  },

  async create(data: {
    bookingReference: string
    companyId: string
    tripId: string
    passengerId: string
    seatId: string
    status: 'PENDING' | 'CONFIRMED'
    source: string
    passengerName: string
    passengerPhone: string
    passengerEmail?: string
    baseFare: number
    seatFee: number
    serviceFee: number
    totalAmount: number
    bookedById?: string
    confirmedAt?: Date
  }) {
    return prisma.booking.create({ data })
  },

  async updateStatus(id: string, status: 'CONFIRMED' | 'CANCELLED', timestampField: 'confirmedAt' | 'cancelledAt') {
    return prisma.booking.update({
      where: { id },
      data: {
        status,
        [timestampField]: new Date()
      }
    })
  }
}