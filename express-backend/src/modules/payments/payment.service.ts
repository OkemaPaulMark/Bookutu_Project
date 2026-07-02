import { paymentRepository } from './payment.repository.js'
import { AppError } from '../../utils/AppError.js'
import { createReference } from '../../utils/ids.js'
import { prisma } from '../../config/prisma.js'

export const paymentService = {
  async listPayments(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    userId: string
    companyId?: string | null
    status?: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'REFUNDED'
    method?: 'CASH' | 'MOBILE_MONEY' | 'CARD' | 'BANK_TRANSFER' | 'WALLET'
    page?: number
    limit?: number
  }) {
    const page = input.page ?? 1
    const limit = input.limit ?? 20
    const skip = (page - 1) * limit

    if (input.userType === 'SUPER_ADMIN') {
      return paymentRepository.findPayments({ status: input.status, method: input.method, skip, take: limit })
    }

    if (input.userType === 'COMPANY_STAFF') {
      return paymentRepository.findPayments({
        companyId: input.companyId,
        status: input.status,
        method: input.method,
        skip,
        take: limit
      })
    }

    return paymentRepository.findPayments({ userId: input.userId, status: input.status, method: input.method, skip, take: limit })
  },

  async createPayment(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    userId: string
    companyId?: string | null
    body: {
      bookingId: string
      paymentMethod: 'CASH' | 'MOBILE_MONEY' | 'CARD' | 'BANK_TRANSFER' | 'WALLET'
      amount?: number
      mobileMoneyNumber?: string
      mobileMoneyProvider?: string
    }
  }) {
    return prisma.$transaction(async (tx) => {
      const booking = await tx.booking.findUnique({ where: { id: input.body.bookingId } })
      if (!booking) throw new AppError(404, 'Booking not found')

      if (
        input.userType !== 'SUPER_ADMIN' &&
        booking.companyId !== input.companyId &&
        booking.passengerId !== input.userId
      ) {
        throw new AppError(403, 'Insufficient permissions')
      }

      // Idempotency: block duplicate payment for same booking
      const existingPayment = await tx.payment.findFirst({
        where: { bookingId: booking.id, status: { in: ['PENDING', 'PROCESSING', 'COMPLETED'] } },
        select: { id: true, status: true }
      })
      if (existingPayment) {
        throw new AppError(409, `A ${existingPayment.status.toLowerCase()} payment already exists for this booking`)
      }

      const amount = input.body.amount ?? Number(booking.totalAmount)
      const status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'REFUNDED' =
        input.body.paymentMethod === 'CASH' ? 'COMPLETED' : 'PENDING'

      const payment = await tx.payment.create({
        data: {
          paymentReference: createReference('PAY'),
          companyId: booking.companyId,
          bookingId: booking.id,
          userId: input.userId,
          amount,
          paymentMethod: input.body.paymentMethod,
          status,
          mobileMoneyNumber: input.body.mobileMoneyNumber,
          mobileMoneyProvider: input.body.mobileMoneyProvider,
          completedAt: status === 'COMPLETED' ? new Date() : undefined
        }
      })

      if (status === 'COMPLETED' && booking.status === 'PENDING') {
        await tx.booking.update({
          where: { id: booking.id },
          data: { status: 'CONFIRMED', confirmedAt: new Date() }
        })

        await tx.trip.update({
          where: { id: booking.tripId },
          data: {
            bookedSeats: { increment: 1 },
            availableSeats: { decrement: 1 }
          }
        })
      }

      return payment
    })
  }
}