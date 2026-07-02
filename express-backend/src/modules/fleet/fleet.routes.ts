import { Router } from 'express'
import {
  createBusController,
  getBusController,
  listBusesController,
  updateBusController,
  listRoutesController,
  getRouteController,
  createRouteController,
  updateRouteController,
  listDriversController,
  getDriverController,
  createDriverController,
  updateDriverController
} from './fleet.controller.js'
import { requireAuth, requireRole } from '../../middlewares/auth.middleware.js'

export const fleetRouter = Router()

// Buses
fleetRouter.get('/buses', requireAuth, listBusesController)
fleetRouter.get('/buses/:id', requireAuth, getBusController)
fleetRouter.post('/buses', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF']), createBusController)
fleetRouter.patch('/buses/:id', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF']), updateBusController)

// Routes
fleetRouter.get('/routes', requireAuth, listRoutesController)
fleetRouter.get('/routes/:id', requireAuth, getRouteController)
fleetRouter.post('/routes', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF']), createRouteController)
fleetRouter.patch('/routes/:id', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF']), updateRouteController)

// Drivers
fleetRouter.get('/drivers', requireAuth, listDriversController)
fleetRouter.get('/drivers/:id', requireAuth, getDriverController)
fleetRouter.post('/drivers', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF']), createDriverController)
fleetRouter.patch('/drivers/:id', requireAuth, requireRole(['SUPER_ADMIN', 'COMPANY_STAFF']), updateDriverController)
