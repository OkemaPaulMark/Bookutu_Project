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
  }) {
    if (input.userType === 'SUPER_ADMIN') {
      return paymentRepository.findPayments({ status: input.status, method: input.method })
    }

    if (input.userType === 'COMPANY_STAFF') {
      return paymentRepository.findPayments({
        companyId: input.companyId,
        status: input.status,
        method: input.method
      })
    }

    return paymentRepository.findPayments({ userId: input.userId, status: input.status, method: input.method })
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
    const booking = await prisma.booking.findUnique({ where: { id: input.body.bookingId } })
    if (!booking) {
      throw new AppError(404, 'Booking not found')
    }

    if (
      input.userType !== 'SUPER_ADMIN' &&
      booking.companyId !== input.companyId &&
      booking.passengerId !== input.userId
    ) {
      throw new AppError(403, 'Insufficient permissions')
    }

    const amount = input.body.amount ?? Number(booking.totalAmount)
    const status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'REFUNDED' =
      input.body.paymentMethod === 'CASH' ? 'COMPLETED' : 'PENDING'

    const payment = await paymentRepository.create({
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
    })

    if (status === 'COMPLETED' && booking.status === 'PENDING') {
      await prisma.booking.update({
        where: { id: booking.id },
        data: {
          status: 'CONFIRMED',
          confirmedAt: new Date()
        }
      })

      await prisma.trip.update({
        where: { id: booking.tripId },
        data: { bookedSeats: { increment: 1 } }
      })
    }

    return payment
  }
}