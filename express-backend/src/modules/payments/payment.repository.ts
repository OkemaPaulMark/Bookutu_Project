import { prisma } from '../../config/prisma.js'

export const paymentRepository = {
  async findPayments(params: {
    companyId?: string | null
    userId?: string
    status?: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'REFUNDED'
    method?: 'CASH' | 'MOBILE_MONEY' | 'CARD' | 'BANK_TRANSFER' | 'WALLET'
    skip?: number
    take?: number
  }) {
    return prisma.payment.findMany({
      where: {
        companyId: params.companyId ?? undefined,
        userId: params.userId,
        status: params.status,
        paymentMethod: params.method
      },
      include: {
        booking: {
          include: {
            trip: { include: { route: true } }
          }
        },
        user: { select: { id: true, email: true, firstName: true, lastName: true } }
      },
      orderBy: { createdAt: 'desc' },
      skip: params.skip,
      take: params.take
    })
  },

  async create(data: {
    paymentReference: string
    companyId: string
    bookingId: string
    userId: string
    amount: number
    currency?: string
    paymentMethod: 'CASH' | 'MOBILE_MONEY' | 'CARD' | 'BANK_TRANSFER' | 'WALLET'
    status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'REFUNDED'
    mobileMoneyNumber?: string
    mobileMoneyProvider?: string
    completedAt?: Date
  }) {
    return prisma.payment.create({ data })
  }
}