import type { Request, Response } from 'express'
import { paymentService } from './payment.service.js'
import { AppError } from '../../utils/AppError.js'

export async function listPaymentsController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const payments = await paymentService.listPayments({
    userType: req.authUser.userType,
    userId: req.authUser.id,
    companyId: req.authUser.companyId,
    status: typeof req.query.status === 'string'
      ? req.query.status as 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'REFUNDED'
      : undefined,
    method: typeof req.query.method === 'string'
      ? req.query.method as 'CASH' | 'MOBILE_MONEY' | 'CARD' | 'BANK_TRANSFER' | 'WALLET'
      : undefined
  })

  res.json({ data: payments })
}

export async function createPaymentController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const payment = await paymentService.createPayment({
    userType: req.authUser.userType,
    userId: req.authUser.id,
    companyId: req.authUser.companyId,
    body: req.body
  })

  res.status(201).json({ data: payment })
}
