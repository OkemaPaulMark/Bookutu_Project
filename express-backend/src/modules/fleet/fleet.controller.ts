import type { Request, Response } from 'express'
import { fleetService } from './fleet.service.js'
import { AppError } from '../../utils/AppError.js'

export async function listBusesController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const buses = await fleetService.listBuses({
    userType: req.authUser.userType,
    companyId: req.authUser.companyId
  })
  res.json({ data: buses })
}

export async function getBusController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const bus = await fleetService.getBus({
    id: String(req.params.id),
    userType: req.authUser.userType,
    companyId: req.authUser.companyId
  })
  res.json({ data: bus })
}

export async function createBusController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const bus = await fleetService.createBus({
    userType: req.authUser.userType,
    companyId: req.authUser.companyId,
    body: req.body
  })
  res.status(201).json({ data: bus })
}

export async function updateBusController(req: Request, res: Response) {
  if (!req.authUser) {
    throw new AppError(401, 'Authentication required')
  }

  const bus = await fleetService.updateBus({
    id: String(req.params.id),
    userType: req.authUser.userType,
    companyId: req.authUser.companyId,
    body: req.body
  })
  res.json({ data: bus })
}
