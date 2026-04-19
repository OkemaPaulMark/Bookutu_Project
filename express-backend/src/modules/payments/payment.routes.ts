import { Router } from 'express'
import { createPaymentController, listPaymentsController } from './payment.controller.js'
import { requireAuth, requireRole } from '../../middlewares/auth.middleware.js'

export const paymentRouter = Router()

paymentRouter.get('/', requireAuth, listPaymentsController)
paymentRouter.post('/', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF', 'PASSENGER']), createPaymentController)
