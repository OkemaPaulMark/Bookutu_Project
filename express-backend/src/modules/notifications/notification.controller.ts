import type { Request, Response } from 'express'
import { notificationService } from './notification.service.js'
import { AppError } from '../../utils/AppError.js'

export async function listNotificationsController(_req: Request, res: Response) {
  if (!_req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const notifications = await notificationService.listAnnouncements({
    userType: _req.authUser.userType,
    includeInactive: (_req.query.all as string | undefined) === 'true'
  })

  res.json({ data: notifications })
}

export async function createNotificationController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const announcement = await notificationService.createAnnouncement({
    userType: req.authUser.userType,
    userId: req.authUser.id,
    body: req.body
  })

  res.status(201).json({ data: announcement })
}

export async function listSystemLogsController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const logs = await notificationService.listSystemLogs({
    userType: req.authUser.userType,
    limit: req.query.limit ? Number(req.query.limit) : undefined
  })

  res.json({ data: logs })
}
