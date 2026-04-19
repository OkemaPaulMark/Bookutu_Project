import { notificationRepository } from './notification.repository.js'
import { AppError } from '../../utils/AppError.js'

export const notificationService = {
  async listAnnouncements(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    includeInactive?: boolean
  }) {
    return notificationRepository.findAnnouncements({
      userType: input.userType,
      includeInactive: input.includeInactive
    })
  },

  async createAnnouncement(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    userId: string
    body: {
      title: string
      message: string
      priority?: string
      targetAudience?: string
      expiresAt?: string
      isActive?: boolean
    }
  }) {
    if (input.userType !== 'SUPER_ADMIN') {
      throw new AppError(403, 'Only super admins can create announcements')
    }

    return notificationRepository.createAnnouncement({
      title: input.body.title,
      message: input.body.message,
      priority: input.body.priority ?? 'medium',
      targetAudience: input.body.targetAudience ?? 'all',
      createdById: input.userId,
      expiresAt: input.body.expiresAt ? new Date(input.body.expiresAt) : undefined,
      isActive: input.body.isActive ?? true
    })
  },

  async listSystemLogs(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    limit?: number
  }) {
    if (input.userType !== 'SUPER_ADMIN') {
      throw new AppError(403, 'Only super admins can access system logs')
    }

    return notificationRepository.findSystemLogs(input.limit ?? 100)
  }
}