import { Router } from 'express'
import {
	bootstrapSuperAdminController,
	changePasswordController,
	getPasswordSetupDetailsController,
	loginController,
	logoutController,
	meController,
	refreshController,
	registerCompanyStaffController,
	registerPassengerController,
	setPasswordController,
	updateProfileController
} from './auth.controller.js'
import { requireAuth, requireRole } from '../../middlewares/auth.middleware.js'

export const authRouter = Router()

authRouter.post('/login', loginController)
authRouter.post('/refresh', refreshController)
authRouter.post('/logout', logoutController)
authRouter.post('/register', registerPassengerController)
authRouter.post('/bootstrap-super-admin', bootstrapSuperAdminController)
authRouter.get('/password-setup/:token', getPasswordSetupDetailsController)
authRouter.post('/set-password', setPasswordController)
authRouter.post('/register/staff', requireAuth, requireRole(['SUPER_ADMIN']), registerCompanyStaffController)
authRouter.get('/me', requireAuth, meController)
authRouter.patch('/me', requireAuth, updateProfileController)
authRouter.patch('/me/password', requireAuth, changePasswordController)
