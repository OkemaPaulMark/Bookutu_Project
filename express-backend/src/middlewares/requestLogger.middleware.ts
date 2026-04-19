import type { NextFunction, Request, Response } from 'express'

export function requestLogger(req: Request, _res: Response, next: NextFunction) {
  req.logContext = {
    method: req.method,
    path: req.path,
    timestamp: new Date().toISOString()
  }

  next()
}
