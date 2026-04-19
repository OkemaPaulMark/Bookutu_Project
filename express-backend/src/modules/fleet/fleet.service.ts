import { fleetRepository } from './fleet.repository.js'
import { AppError } from '../../utils/AppError.js'

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
    const existing = await this.getBus({
      id: input.id,
      userType: input.userType,
      companyId: input.companyId
    })

    return fleetRepository.update(existing.id, input.body)
  }
}