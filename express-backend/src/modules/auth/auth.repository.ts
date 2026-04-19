import { prisma } from '../../config/prisma.js'

export const authRepository = {
  async findUserByEmail(email: string) {
    return prisma.user.findUnique({
      where: { email },
      include: {
        company: {
          select: { id: true, name: true, status: true }
        }
      }
    })
  },

  async findUserById(id: string) {
    return prisma.user.findUnique({
      where: { id },
      include: {
        company: {
          select: { id: true, name: true, status: true }
        }
      }
    })
  },

  async createUser(data: {
    email: string
    username?: string
    firstName?: string
    lastName?: string
    phoneNumber?: string
    passwordHash: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string
    isVerified?: boolean
  }) {
    return prisma.user.create({ data })
  }
}
