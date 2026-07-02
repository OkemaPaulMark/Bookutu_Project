import { bookingRepository } from './booking.repository.js'
import { AppError } from '../../utils/AppError.js'
import { prisma } from '../../config/prisma.js'
import { createReference } from '../../utils/ids.js'

export const bookingService = {
  async listBookings(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    userId: string
    companyId?: string | null
    status?: 'PENDING' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW'
    search?: string
    page?: number
    limit?: number
  }) {
    const page = input.page ?? 1
    const limit = input.limit ?? 20
    const skip = (page - 1) * limit

    if (input.userType === 'SUPER_ADMIN') {
      return bookingRepository.findBookings({ status: input.status, search: input.search, skip, take: limit })
    }

    if (input.userType === 'COMPANY_STAFF') {
      return bookingRepository.findBookings({
        companyId: input.companyId,
        status: input.status,
        search: input.search,
        skip,
        take: limit
      })
    }

    return prisma.booking.findMany({
      where: { passengerId: input.userId },
      include: { trip: true, seat: true },
      orderBy: { createdAt: 'desc' },
      skip,
      take: limit
    })
  },

  async getBooking(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    userId: string
    companyId?: string | null
  }) {
    const booking = await bookingRepository.findById(input.id)
    if (!booking) {
      throw new AppError(404, 'Booking not found')
    }

    if (input.userType === 'SUPER_ADMIN') return booking
    if (input.userType === 'COMPANY_STAFF' && booking.companyId === input.companyId) return booking
    if (input.userType === 'PASSENGER' && booking.passengerId === input.userId) return booking

    throw new AppError(403, 'Insufficient permissions')
  },

  async createBooking(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    userId: string
    companyId?: string | null
    body: {
      tripId: string
      seatId: string
      passengerName: string
      passengerPhone: string
      passengerEmail?: string
      source?: string
    }
  }) {
    return prisma.$transaction(async (tx) => {
      const trip = await tx.trip.findUnique({
        where: { id: input.body.tripId },
        include: { bus: true }
      })

      if (!trip) throw new AppError(404, 'Trip not found')

      if (input.userType !== 'SUPER_ADMIN' && input.companyId !== trip.companyId && input.userType !== 'PASSENGER') {
        throw new AppError(403, 'Insufficient permissions')
      }

      if (trip.status !== 'SCHEDULED') throw new AppError(400, 'Trip is not available for booking')

      if (trip.availableSeats <= 0) throw new AppError(409, 'No seats available on this trip')

      const seat = await tx.busSeat.findUnique({ where: { id: input.body.seatId } })
      if (!seat || seat.busId !== trip.busId) throw new AppError(400, 'Invalid seat for trip bus')

      // Idempotency: check for existing active booking on this seat+trip
      const existingBooking = await tx.booking.findFirst({
        where: { tripId: trip.id, seatId: seat.id, status: { in: ['PENDING', 'CONFIRMED'] } },
        select: { id: true }
      })
      if (existingBooking) throw new AppError(409, 'Seat is already booked')

      const baseFare = Number(trip.baseFare)
      const totalAmount = baseFare

      const status = input.userType === 'COMPANY_STAFF' ? 'CONFIRMED' : 'PENDING'

      const booking = await tx.booking.create({
        data: {
          bookingReference: createReference('BK'),
          companyId: trip.companyId,
          tripId: trip.id,
          passengerId: input.userId,
          seatId: seat.id,
          status,
          source: input.body.source ?? (input.userType === 'COMPANY_STAFF' ? 'DIRECT' : 'MOBILE_APP'),
          passengerName: input.body.passengerName,
          passengerPhone: input.body.passengerPhone,
          passengerEmail: input.body.passengerEmail,
          baseFare,
          seatFee: 0,
          serviceFee: 0,
          totalAmount,
          bookedById: input.userType === 'COMPANY_STAFF' ? input.userId : undefined,
          confirmedAt: status === 'CONFIRMED' ? new Date() : undefined
        }
      })

      if (status === 'CONFIRMED') {
        await tx.trip.update({
          where: { id: trip.id },
          data: {
            bookedSeats: { increment: 1 },
            availableSeats: { decrement: 1 }
          }
        })
      }

      return tx.booking.findUnique({
        where: { id: booking.id },
        include: {
          trip: { include: { route: true, bus: true } },
          seat: true,
          passenger: { select: { id: true, email: true, firstName: true, lastName: true } },
          payments: true
        }
      })
    })
  },

  async cancelBooking(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    userId: string
    companyId?: string | null
  }) {
    const booking = await this.getBooking(input)

    if (!['PENDING', 'CONFIRMED'].includes(booking.status)) {
      throw new AppError(400, 'Booking cannot be cancelled in its current status')
    }

    return prisma.$transaction(async (tx) => {
      const cancelled = await tx.booking.update({
        where: { id: booking.id },
        data: { status: 'CANCELLED', cancelledAt: new Date() }
      })

      if (booking.status === 'CONFIRMED') {
        await tx.trip.update({
          where: { id: booking.tripId },
          data: {
            bookedSeats: { decrement: 1 },
            availableSeats: { increment: 1 }
          }
        })
      }

      return cancelled
    })
  }
}