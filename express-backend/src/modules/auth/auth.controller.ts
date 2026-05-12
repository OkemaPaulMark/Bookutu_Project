import type { Request, Response } from 'express'
import { authService } from './auth.service.js'
import {
  bootstrapSuperAdminSchema,
  inviteCompanyAdminSchema,
  loginSchema,
  registerPassengerSchema,
  setPasswordSchema
} from './auth.validators.js'
import { AppError } from '../../utils/AppError.js'

export async function loginController(req: Request, res: Response) {
  const payload = loginSchema.parse(req.body)
  const data = await authService.login(payload)
  res.json(data)
}

export async function refreshController(req: Request, res: Response) {
  const refreshToken = req.body?.refresh as string | undefined
  if (!refreshToken) {
    throw new AppError(400, 'refresh token is required')
  }

  const data = await authService.refresh(refreshToken)
  res.json(data)
}

export async function meController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const user = await authService.me(req.authUser.id)
  res.json({ user })
}

export async function registerPassengerController(req: Request, res: Response) {
  const payload = registerPassengerSchema.parse(req.body)
  const data = await authService.registerPassenger(payload)
  res.status(201).json(data)
}

export async function registerCompanyStaffController(req: Request, res: Response) {
  const payload = inviteCompanyAdminSchema.parse(req.body)
  const data = await authService.inviteCompanyAdmin(payload)
  res.status(201).json(data)
}

export async function getPasswordSetupDetailsController(req: Request, res: Response) {
  const token = String(req.params.token)
  const data = await authService.getPasswordSetupDetails(token)
  res.json(data)
}

export async function setPasswordController(req: Request, res: Response) {
  const payload = setPasswordSchema.parse(req.body)
  const data = await authService.setPassword(payload)
  res.json(data)
}

export async function bootstrapSuperAdminController(req: Request, res: Response) {
  const payload = bootstrapSuperAdminSchema.parse(req.body)
  const data = await authService.bootstrapSuperAdmin(payload)
  res.status(201).json(data)
}
