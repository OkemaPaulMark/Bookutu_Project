import type { Request, Response } from 'express'
import { bookingService } from './booking.service.js'
import { AppError } from '../../utils/AppError.js'

export async function listBookingsController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const bookings = await bookingService.listBookings({
    userType: req.authUser.userType,
    userId: req.authUser.id,
    companyId: req.authUser.companyId,
    status: typeof req.query.status === 'string'
      ? req.query.status as 'PENDING' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW'
      : undefined,
    search: typeof req.query.search === 'string' ? req.query.search : undefined
  })
  res.json({ data: bookings })
}

export async function getBookingController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const booking = await bookingService.getBooking({
    id: String(req.params.id),
    userType: req.authUser.userType,
    userId: req.authUser.id,
    companyId: req.authUser.companyId
  })

  res.json({ data: booking })
}

export async function createBookingController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const booking = await bookingService.createBooking({
    userType: req.authUser.userType,
    userId: req.authUser.id,
    companyId: req.authUser.companyId,
    body: req.body
  })

  res.status(201).json({ data: booking })
}

export async function cancelBookingController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const booking = await bookingService.cancelBooking({
    id: String(req.params.id),
    userType: req.authUser.userType,
    userId: req.authUser.id,
    companyId: req.authUser.companyId
  })

  res.json({ data: booking })
}
