import { Router } from 'express'
import {
	createTripController,
	getTripController,
	listTripsController,
	tripManifestController,
	tripStatsController,
	updateTripController
} from './trip.controller.js'
import { requireAuth, requireRole } from '../../middlewares/auth.middleware.js'

export const tripRouter = Router()

tripRouter.get('/', requireAuth, listTripsController)
tripRouter.get('/dashboard/stats', requireAuth, requireRole(['COMPANY_STAFF', 'SUPER_ADMIN']), tripStatsController)
tripRouter.get('/:id', requireAuth, getTripController)
tripRouter.get('/:id/manifest', requireAuth, requireRole(['COMPANY_STAFF', 'SUPER_ADMIN']), tripManifestController)
tripRouter.post('/', requireAuth, requireRole(['COMPANY_STAFF', 'SUPER_ADMIN']), createTripController)
tripRouter.patch('/:id', requireAuth, requireRole(['COMPANY_STAFF', 'SUPER_ADMIN']), updateTripController)
