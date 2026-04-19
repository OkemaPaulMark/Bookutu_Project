import { Router } from 'express'
import {
	loginController,
	meController,
	refreshController,
	registerCompanyStaffController,
	registerPassengerController
} from './auth.controller.js'
import { requireAuth, requireRole } from '../../middlewares/auth.middleware.js'

export const authRouter = Router()

authRouter.post('/login', loginController)
authRouter.post('/refresh', refreshController)
authRouter.post('/register', registerPassengerController)
authRouter.post('/register/staff', requireAuth, requireRole(['SUPER_ADMIN']), registerCompanyStaffController)
authRouter.get('/me', requireAuth, meController)
