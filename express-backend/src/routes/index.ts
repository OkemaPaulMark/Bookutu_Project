import { Router } from 'express'
import { healthRouter } from './health.routes.js'
import { authRouter } from '../modules/auth/auth.routes.js'
import { companyRouter } from '../modules/companies/company.routes.js'
import { fleetRouter } from '../modules/fleet/fleet.routes.js'
import { tripRouter } from '../modules/trips/trip.routes.js'
import { bookingRouter } from '../modules/bookings/booking.routes.js'
import { paymentRouter } from '../modules/payments/payment.routes.js'
import { notificationRouter } from '../modules/notifications/notification.routes.js'

export const apiRoutes = Router()

apiRoutes.use('/health', healthRouter)
apiRoutes.use('/auth', authRouter)
apiRoutes.use('/companies', companyRouter)
apiRoutes.use('/fleet', fleetRouter)
apiRoutes.use('/trips', tripRouter)
apiRoutes.use('/bookings', bookingRouter)
apiRoutes.use('/payments', paymentRouter)
apiRoutes.use('/notifications', notificationRouter)
