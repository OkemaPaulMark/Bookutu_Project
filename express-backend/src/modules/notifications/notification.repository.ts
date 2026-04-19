import { prisma } from '../../config/prisma.js'

export const notificationRepository = {
  async findAnnouncements(params: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    includeInactive?: boolean
  }) {
    const now = new Date()
    return prisma.announcement.findMany({
      where: {
        isActive: params.includeInactive ? undefined : true,
        OR: params.includeInactive
          ? undefined
          : [
              { expiresAt: null },
              { expiresAt: { gte: now } }
            ],
        targetAudience:
          params.userType === 'SUPER_ADMIN'
            ? undefined
            : params.userType === 'COMPANY_STAFF'
              ? { in: ['all', 'companies', 'staff'] }
              : { in: ['all', 'passengers'] }
      },
      include: {
        createdBy: { select: { id: true, email: true, firstName: true, lastName: true } }
      },
      orderBy: { createdAt: 'desc' }
    })
  },

  async createAnnouncement(data: {
    title: string
    message: string
    priority: string
    targetAudience: string
    createdById: string
    expiresAt?: Date
    isActive?: boolean
  }) {
    return prisma.announcement.create({ data })
  },

  async findSystemLogs(limit = 100) {
    return prisma.systemLog.findMany({
      include: {
        user: { select: { id: true, email: true, firstName: true, lastName: true } }
      },
      orderBy: { createdAt: 'desc' },
      take: limit
    })
  }
}