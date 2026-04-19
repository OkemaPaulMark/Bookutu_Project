import { Router } from 'express'
import {
	createBusController,
	getBusController,
	listBusesController,
	updateBusController
} from './fleet.controller.js'
import { requireAuth, requireRole } from '../../middlewares/auth.middleware.js'

export const fleetRouter = Router()

fleetRouter.get('/buses', requireAuth, listBusesController)
fleetRouter.get('/buses/:id', requireAuth, getBusController)
fleetRouter.post('/buses', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF']), createBusController)
fleetRouter.patch('/buses/:id', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF']), updateBusController)
