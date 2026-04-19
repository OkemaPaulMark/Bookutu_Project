import { Router } from 'express'
import {
	createCompanyController,
	getCompanyController,
	listCompaniesController,
	updateCompanyController
} from './company.controller.js'
import { requireAuth, requireRole } from '../../middlewares/auth.middleware.js'

export const companyRouter = Router()

companyRouter.get('/', requireAuth, listCompaniesController)
companyRouter.get('/:id', requireAuth, getCompanyController)
companyRouter.post('/', requireAuth, requireRole(['SUPER_ADMIN']), createCompanyController)
companyRouter.patch('/:id', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF']), updateCompanyController)
