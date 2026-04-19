import type { Request, Response } from 'express'
import { tripService } from './trip.service.js'
import { AppError } from '../../utils/AppError.js'

export async function listTripsController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const trips = await tripService.listTrips({
    userType: req.authUser.userType,
    companyId: req.authUser.companyId,
    status: req.query.status as string | undefined,
    departureDate: req.query.departureDate as string | undefined,
    routeId: req.query.routeId as string | undefined
  })

  res.json({ data: trips })
}

export async function getTripController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const trip = await tripService.getTrip({
    id: Array.isArray(req.params.id) ? req.params.id[0] : req.params.id,
    userType: req.authUser.userType,
    companyId: req.authUser.companyId
  })

  res.json({ data: trip })
}

export async function createTripController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const trip = await tripService.createTrip({
    userType: req.authUser.userType,
    companyId: req.authUser.companyId,
    body: req.body
  })

  res.status(201).json({ data: trip })
}

export async function updateTripController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const trip = await tripService.updateTrip({
    id: Array.isArray(req.params.id) ? req.params.id[0] : req.params.id,
    userType: req.authUser.userType,
    companyId: req.authUser.companyId,
    body: req.body
  })

  res.json({ data: trip })
}

export async function tripManifestController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const manifest = await tripService.manifest({
    id: Array.isArray(req.params.id) ? req.params.id[0] : req.params.id,
    userType: req.authUser.userType,
    companyId: req.authUser.companyId
  })

  res.json({ data: manifest })
}

export async function tripStatsController(req: Request, res: Response) {
  if (!req.authUser?.companyId) {
    throw new AppError(400, 'company scope required')
  }

  const stats = await tripService.dashboardStats({ companyId: req.authUser.companyId })
  res.json({ data: stats })
}
