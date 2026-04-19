import { companyRepository } from './company.repository.js'
import { AppError } from '../../utils/AppError.js'
import { toSlug } from '../../utils/slug.js'

export const companyService = {
  async listCompanies(input: {
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
    search?: string
    status?: 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'INACTIVE'
  }) {
    if (input.userType === 'SUPER_ADMIN') {
      return companyRepository.findAll({
        search: input.search,
        status: input.status
      })
    }

    if (!input.companyId) {
      return []
    }

    const company = await companyRepository.findById(input.companyId)
    return company ? [company] : []
  },

  async getCompany(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
  }) {
    if (input.userType !== 'SUPER_ADMIN' && input.companyId !== input.id) {
      throw new AppError(403, 'Insufficient permissions')
    }

    const company = await companyRepository.findById(input.id)
    if (!company) {
      throw new AppError(404, 'Company not found')
    }

    return company
  },

  async createCompany(input: {
    name: string
    description?: string
    email: string
    phoneNumber: string
    website?: string
    address: string
    city: string
    state: string
    country?: string
    postalCode?: string
    registrationNumber: string
    taxId?: string
    licenseNumber: string
    commissionRate?: number
  }) {
    const baseSlug = toSlug(input.name)
    let slug = baseSlug || 'company'
    let suffix = 1

    while (await companyRepository.findBySlug(slug)) {
      suffix += 1
      slug = `${baseSlug}-${suffix}`
    }

    return companyRepository.create({
      ...input,
      slug
    })
  },

  async updateCompany(input: {
    id: string
    userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
    companyId?: string | null
    data: Partial<{
      name: string
      description: string
      email: string
      phoneNumber: string
      website: string
      address: string
      city: string
      state: string
      country: string
      postalCode: string
      taxId: string
      licenseNumber: string
      commissionRate: number
      status: 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'INACTIVE'
    }>
  }) {
    if (input.userType !== 'SUPER_ADMIN' && input.companyId !== input.id) {
      throw new AppError(403, 'Insufficient permissions')
    }

    return companyRepository.update(input.id, input.data)
  }
}
