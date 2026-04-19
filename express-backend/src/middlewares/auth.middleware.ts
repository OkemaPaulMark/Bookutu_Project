import type { NextFunction, Request, Response } from 'express'
import { AppError } from '../utils/AppError.js'
import { verifyAccessToken } from '../utils/token.js'

export function requireAuth(req: Request, _res: Response, next: NextFunction) {
  const authorization = req.headers.authorization

  if (!authorization?.startsWith('Bearer ')) {
    return next(new AppError(401, 'Authentication required'))
  }

  const token = authorization.slice(7)

  try {
    const payload = verifyAccessToken(token)
    req.authUser = {
      id: payload.sub,
      userType: payload.userType,
      companyId: payload.companyId ?? null
    }
  } catch {
    return next(new AppError(401, 'Invalid or expired token'))
  }

  return next()
}

export function requireRole(roles: Array<'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'>) {
  return (req: Request, _res: Response, next: NextFunction) => {
    if (!req.authUser) {
      return next(new AppError(401, 'Authentication required'))
    }

    if (!roles.includes(req.authUser.userType)) {
      return next(new AppError(403, 'Insufficient permissions'))
    }

    return next()
  }
}
