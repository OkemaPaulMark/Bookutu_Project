import { Router } from 'express'
import {
	createNotificationController,
	listNotificationsController,
	listSystemLogsController
} from './notification.controller.js'
import { requireAuth, requireRole } from '../../middlewares/auth.middleware.js'

export const notificationRouter = Router()

notificationRouter.get('/', requireAuth, listNotificationsController)
notificationRouter.post('/', requireAuth, requireRole(['SUPER_ADMIN']), createNotificationController)
notificationRouter.get('/logs', requireAuth, requireRole(['SUPER_ADMIN']), listSystemLogsController)
