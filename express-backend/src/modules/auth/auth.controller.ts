import type { Request, Response } from 'express'
import { authService } from './auth.service.js'
import { loginSchema } from './auth.validators.js'
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
  const user = await authService.registerPassenger(req.body)
  res.status(201).json({ user })
}

export async function registerCompanyStaffController(req: Request, res: Response) {
  const user = await authService.registerCompanyStaff(req.body)
  res.status(201).json({ user })
}
