import { Router } from 'express'
import {
	cancelBookingController,
	createBookingController,
	getBookingController,
	listBookingsController
} from './booking.controller.js'
import { requireAuth, requireRole } from '../../middlewares/auth.middleware.js'

export const bookingRouter = Router()

bookingRouter.get('/', requireAuth, listBookingsController)
bookingRouter.get('/:id', requireAuth, getBookingController)
bookingRouter.post('/', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF', 'PASSENGER']), createBookingController)
bookingRouter.patch('/:id/cancel', requireAuth, cancelBookingController)
