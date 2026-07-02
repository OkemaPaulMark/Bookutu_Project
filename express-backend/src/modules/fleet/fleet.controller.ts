import type { Request, Response } from 'express'
import { fleetService } from './fleet.service.js'
import { AppError } from '../../utils/AppError.js'

export async function listBusesController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const buses = await fleetService.listBuses({ userType: req.authUser.userType, companyId: req.authUser.companyId })
  res.json({ data: buses })
}

export async function getBusController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const bus = await fleetService.getBus({ id: String(req.params.id), userType: req.authUser.userType, companyId: req.authUser.companyId })
  res.json({ data: bus })
}

export async function createBusController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const bus = await fleetService.createBus({ userType: req.authUser.userType, companyId: req.authUser.companyId, body: req.body })
  res.status(201).json({ data: bus })
}

export async function updateBusController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const bus = await fleetService.updateBus({ id: String(req.params.id), userType: req.authUser.userType, companyId: req.authUser.companyId, body: req.body })
  res.json({ data: bus })
}

// Routes
export async function listRoutesController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const routes = await fleetService.listRoutes({ userType: req.authUser.userType, companyId: req.authUser.companyId })
  res.json({ data: routes })
}

export async function getRouteController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const route = await fleetService.getRoute({ id: String(req.params.id), userType: req.authUser.userType, companyId: req.authUser.companyId })
  res.json({ data: route })
}

export async function createRouteController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const route = await fleetService.createRoute({ userType: req.authUser.userType, companyId: req.authUser.companyId, body: req.body })
  res.status(201).json({ data: route })
}

export async function updateRouteController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const route = await fleetService.updateRoute({ id: String(req.params.id), userType: req.authUser.userType, companyId: req.authUser.companyId, body: req.body })
  res.json({ data: route })
}

// Drivers
export async function listDriversController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const drivers = await fleetService.listDrivers({ userType: req.authUser.userType, companyId: req.authUser.companyId })
  res.json({ data: drivers })
}

export async function getDriverController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const driver = await fleetService.getDriver({ id: String(req.params.id), userType: req.authUser.userType, companyId: req.authUser.companyId })
  res.json({ data: driver })
}

export async function createDriverController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const driver = await fleetService.createDriver({ userType: req.authUser.userType, companyId: req.authUser.companyId, body: req.body })
  res.status(201).json({ data: driver })
}

export async function updateDriverController(req: Request, res: Response) {
  if (!req.authUser) throw new AppError(401, 'Authentication required')
  const driver = await fleetService.updateDriver({ id: String(req.params.id), userType: req.authUser.userType, companyId: req.authUser.companyId, body: req.body })
  res.json({ data: driver })
}
