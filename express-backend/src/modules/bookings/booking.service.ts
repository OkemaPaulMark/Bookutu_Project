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
  }) {
    if (input.userType === 'SUPER_ADMIN') {
      return bookingRepository.findBookings({ 
        status: input.status, 
        search: input.search 
      })
    }

    if (input.userType === 'COMPANY_STAFF') {
      return bookingRepository.findBookings({
        companyId: input.companyId,
        status: input.status,
        search: input.search
      })
    }

    return prisma.booking.findMany({
      where: { passengerId: input.userId },
      include: { trip: true, seat: true },
      orderBy: { createdAt: 'desc' }
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

    if (input.userType === 'SUPER_ADMIN') {
      return booking
    }

    if (input.userType === 'COMPANY_STAFF' && booking.companyId === input.companyId) {
      return booking
    }

    if (input.userType === 'PASSENGER' && booking.passengerId === input.userId) {
      return booking
    }

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
      serviceFee?: number
    }
  }) {
    const trip = await prisma.trip.findUnique({
      where: { id: input.body.tripId },
      include: { bus: true }
    })

    if (!trip) {
      throw new AppError(404, 'Trip not found')
    }

    if (input.userType !== 'SUPER_ADMIN' && input.companyId !== trip.companyId && input.userType !== 'PASSENGER') {
      throw new AppError(403, 'Insufficient permissions')
    }

    if (trip.status !== 'SCHEDULED') {
      throw new AppError(400, 'Trip is not available for booking')
    }

    const seat = await prisma.busSeat.findUnique({ where: { id: input.body.seatId } })
    if (!seat || seat.busId !== trip.busId) {
      throw new AppError(400, 'Invalid seat for trip bus')
    }

    const isBooked = await bookingRepository.seatIsBooked(trip.id, seat.id)
    if (isBooked) {
      throw new AppError(409, 'Seat is already booked')
    }

    const baseFare = Number(trip.baseFare)
    const seatFee = baseFare * (Number(seat.priceMultiplier) - 1)
    const serviceFee = input.body.serviceFee ?? 0
    const totalAmount = baseFare + seatFee + serviceFee

    const status = input.userType === 'COMPANY_STAFF' ? 'CONFIRMED' : 'PENDING'
    const booking = await bookingRepository.create({
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
      seatFee,
      serviceFee,
      totalAmount,
      bookedById: input.userType === 'COMPANY_STAFF' ? input.userId : undefined,
      confirmedAt: status === 'CONFIRMED' ? new Date() : undefined
    })

    await prisma.trip.update({
      where: { id: trip.id },
      data: {
        bookedSeats: { increment: status === 'CONFIRMED' ? 1 : 0 }
      }
    })

    return this.getBooking({
      id: booking.id,
      userType: input.userType,
      userId: input.userId,
      companyId: input.companyId
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

    const cancelled = await bookingRepository.updateStatus(booking.id, 'CANCELLED', 'cancelledAt')

    if (booking.status === 'CONFIRMED') {
      await prisma.trip.update({
        where: { id: booking.tripId },
        data: { bookedSeats: { decrement: 1 } }
      })
    }

    return cancelled
  }
}