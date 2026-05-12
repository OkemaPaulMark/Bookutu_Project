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

  async findUserByUsername(username: string) {
    return prisma.user.findUnique({
      where: { username },
      include: {
        company: {
          select: { id: true, name: true, status: true }
        }
      }
    })
  },

  async findUserByPasswordSetupTokenHash(passwordSetupTokenHash: string) {
    return prisma.user.findFirst({
      where: { passwordSetupTokenHash },
      include: {
        company: {
          select: { id: true, name: true, status: true }
        }
      }
    })
  },

  async countSuperAdmins() {
    return prisma.user.count({
      where: { userType: 'SUPER_ADMIN' }
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
    isActive?: boolean
    passwordSetupTokenHash?: string | null
    passwordSetupTokenExpiresAt?: Date | null
    invitedAt?: Date | null
  }) {
    return prisma.user.create({
      data,
      include: {
        company: {
          select: { id: true, name: true, status: true }
        }
      }
    })
  },

  async updateUser(id: string, data: Partial<{
    email: string
    username: string | null
    firstName: string | null
    lastName: string | null
    phoneNumber: string | null
    passwordHash: string
    companyId: string | null
    isVerified: boolean
    isActive: boolean
    passwordSetupTokenHash: string | null
    passwordSetupTokenExpiresAt: Date | null
    invitedAt: Date | null
  }>) {
    return prisma.user.update({
      where: { id },
      data,
      include: {
        company: {
          select: { id: true, name: true, status: true }
        }
      }
    })
  }
}
