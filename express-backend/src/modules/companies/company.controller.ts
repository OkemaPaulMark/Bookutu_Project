import type { Request, Response } from 'express'
import { companyService } from './company.service.js'
import { AppError } from '../../utils/AppError.js'

export async function listCompaniesController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const status = typeof req.query.status === 'string'
    ? (req.query.status as 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'INACTIVE')
    : undefined
  const search = typeof req.query.search === 'string' ? req.query.search : undefined

  const companies = await companyService.listCompanies({
    userType: req.authUser.userType,
    companyId: req.authUser.companyId,
    search,
    status
  })

  res.json({ data: companies })
}

export async function getCompanyController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const company = await companyService.getCompany({
    id: String(req.params.id),
    userType: req.authUser.userType,
    companyId: req.authUser.companyId
  })

  res.json({ data: company })
}

export async function platformStatsController(req: Request, res: Response) {
  if (!req.authUser || req.authUser.userType !== 'SUPER_ADMIN') {
    throw new AppError(403, 'Super admin only')
  }

  const stats = await companyService.platformStats()
  res.json({ data: stats })
}

export async function createCompanyController(req: Request, res: Response) {
  const company = await companyService.createCompany(req.body)
  res.status(201).json({ data: company })
}

export async function updateCompanyController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const company = await companyService.updateCompany({
    id: String(req.params.id),
    userType: req.authUser.userType,
    companyId: req.authUser.companyId,
    data: req.body
  })

  res.json({ data: company })
}
