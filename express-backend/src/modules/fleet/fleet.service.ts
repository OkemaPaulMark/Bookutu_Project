import { fleetRepository } from './fleet.repository.js'
import { AppError } from '../../utils/AppError.js'

type UserScope = {
  userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
  companyId?: string | null
}

export const fleetService = {
  async listBuses(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
  }) {
    const companyScope = input.userType === 'SUPER_ADMIN' ? undefined : input.companyId
    return fleetRepository.findBuses(companyScope)
  },

  async getBus(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
  }) {
    const bus = await fleetRepository.findById(input.id)
    if (!bus) {
      throw new AppError(404, 'Bus not found')
    }

    if (input.userType !== 'SUPER_ADMIN' && bus.companyId !== input.companyId) {
      throw new AppError(403, 'Insufficient permissions')
    }

    return bus
  },

  async createBus(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
    body: {
      companyId?: string
      licensePlate: string
      model: string
      make: string
      year: number
      totalSeats: number
      busType: string
      hasAc?: boolean
      hasWifi?: boolean
      hasChargingPorts?: boolean
      hasEntertainment?: boolean
      hasRestroom?: boolean
      imageUrl?: string
    }
  }) {
    const companyId = input.userType === 'SUPER_ADMIN' ? input.body.companyId : input.companyId
    if (!companyId) {
      throw new AppError(400, 'companyId is required')
    }

    const bus = await fleetRepository.create({
      ...input.body,
      companyId
    })

    await fleetRepository.createSeats(bus.id, input.body.totalSeats)
    return fleetRepository.findById(bus.id)
  },

  async updateBus(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
    body: Partial<{
      model: string
      make: string
      year: number
      busType: string
      status: 'ACTIVE' | 'MAINTENANCE' | 'INACTIVE'
      hasAc: boolean
      hasWifi: boolean
      hasChargingPorts: boolean
      hasEntertainment: boolean
      hasRestroom: boolean
      imageUrl: string
    }>
  }) {
    const existing = await this.getBus({ id: input.id, userType: input.userType, companyId: input.companyId })
    return fleetRepository.update(existing.id, input.body)
  },

  // Routes
  async listRoutes(input: UserScope) {
    const companyScope = input.userType === 'SUPER_ADMIN' ? undefined : input.companyId
    return fleetRepository.findRoutes(companyScope)
  },

  async getRoute(input: UserScope & { id: string }) {
    const route = await fleetRepository.findRouteById(input.id)
    if (!route) throw new AppError(404, 'Route not found')
    if (input.userType !== 'SUPER_ADMIN' && route.companyId !== input.companyId) {
      throw new AppError(403, 'Insufficient permissions')
    }
    return route
  },

  async createRoute(input: UserScope & { body: {
    companyId?: string
    name: string
    originCity: string
    originTerminal: string
    destinationCity: string
    destinationTerminal: string
    distanceKm: number
    estimatedDurationHours: number
    baseFare: number
    intermediateStops?: object
  }}) {
    const companyId = input.userType === 'SUPER_ADMIN' ? input.body.companyId : input.companyId
    if (!companyId) throw new AppError(400, 'companyId is required')
    return fleetRepository.createRoute({ ...input.body, companyId })
  },

  async updateRoute(input: UserScope & { id: string, body: Partial<{
    name: string
    originCity: string
    originTerminal: string
    destinationCity: string
    destinationTerminal: string
    distanceKm: number
    estimatedDurationHours: number
    baseFare: number
    isActive: boolean
    intermediateStops: object
  }>}) {
    await this.getRoute({ id: input.id, userType: input.userType, companyId: input.companyId })
    return fleetRepository.updateRoute(input.id, input.body)
  },

  // Drivers
  async listDrivers(input: UserScope) {
    const companyScope = input.userType === 'SUPER_ADMIN' ? undefined : input.companyId
    return fleetRepository.findDrivers(companyScope)
  },

  async getDriver(input: UserScope & { id: string }) {
    const driver = await fleetRepository.findDriverById(input.id)
    if (!driver) throw new AppError(404, 'Driver not found')
    if (input.userType !== 'SUPER_ADMIN' && driver.companyId !== input.companyId) {
      throw new AppError(403, 'Insufficient permissions')
    }
    return driver
  },

  async createDriver(input: UserScope & { body: {
    companyId?: string
    firstName: string
    lastName: string
    phoneNumber: string
    email?: string
    licenseNumber: string
    licenseExpiryDate: string
    dateOfBirth: string
    employeeId?: string
    hireDate: string
  }}) {
    const companyId = input.userType === 'SUPER_ADMIN' ? input.body.companyId : input.companyId
    if (!companyId) throw new AppError(400, 'companyId is required')
    return fleetRepository.createDriver({
      ...input.body,
      companyId,
      licenseExpiryDate: new Date(input.body.licenseExpiryDate),
      dateOfBirth: new Date(input.body.dateOfBirth),
      hireDate: new Date(input.body.hireDate)
    })
  },

  async updateDriver(input: UserScope & { id: string, body: Partial<{
    firstName: string
    lastName: string
    phoneNumber: string
    email: string
    licenseNumber: string
    licenseExpiryDate: string
    status: string
  }>}) {
    await this.getDriver({ id: input.id, userType: input.userType, companyId: input.companyId })
    return fleetRepository.updateDriver(input.id, {
      ...input.body,
      licenseExpiryDate: input.body.licenseExpiryDate ? new Date(input.body.licenseExpiryDate) : undefined
    })
  }
}