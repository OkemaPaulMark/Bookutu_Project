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
  },

  async platformStats() {
    const { prisma } = await import('../../config/prisma.js')

    const [companiesByStatus, totalTrips, totalBookings, revenueAgg,
      recentCompanies, topCompanies] = await Promise.all([
      prisma.company.groupBy({ by: ['status'], _count: { id: true } }),
      prisma.trip.count(),
      prisma.booking.count(),
      prisma.booking.aggregate({
        where: { status: { in: ['CONFIRMED', 'COMPLETED'] } },
        _sum: { totalAmount: true }
      }),
      // 5 most recently registered companies
      prisma.company.findMany({
        orderBy: { createdAt: 'desc' },
        take: 5,
        select: { id: true, name: true, city: true, status: true, createdAt: true }
      }),
      // top 5 companies by booking count
      prisma.company.findMany({
        include: {
          _count: { select: { bookings: true, trips: true, buses: true } }
        },
        orderBy: { bookings: { _count: 'desc' } },
        take: 5
      })
    ])

    // Monthly revenue last 6 months (platform-wide)
    const sixMonthsAgo = new Date()
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 5)
    sixMonthsAgo.setDate(1)
    sixMonthsAgo.setHours(0, 0, 0, 0)
    const recentBookings = await prisma.booking.findMany({
      where: {
        status: { in: ['CONFIRMED', 'COMPLETED'] },
        createdAt: { gte: sixMonthsAgo }
      },
      select: { totalAmount: true, createdAt: true }
    })
    const monthlyMap = new Map<string, number>()
    for (const b of recentBookings) {
      const key = b.createdAt.toISOString().slice(0, 7)
      monthlyMap.set(key, (monthlyMap.get(key) ?? 0) + Number(b.totalAmount))
    }
    const monthlyRevenue = Array.from(monthlyMap.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, revenue]) => ({ month, revenue }))

    const statusMap: Record<string, number> = {}
    for (const g of companiesByStatus) statusMap[g.status] = g._count.id

    return {
      companies: {
        total: Object.values(statusMap).reduce((s, v) => s + v, 0),
        active: statusMap['ACTIVE'] ?? 0,
        pending: statusMap['PENDING'] ?? 0,
        suspended: statusMap['SUSPENDED'] ?? 0,
        inactive: statusMap['INACTIVE'] ?? 0
      },
      totalTrips,
      totalBookings,
      totalRevenue: Number(revenueAgg._sum.totalAmount ?? 0),
      monthlyRevenue,
      recentCompanies,
      topCompanies: topCompanies.map(c => ({
        id: c.id,
        name: c.name,
        city: c.city,
        status: c.status,
        bookings: c._count.bookings,
        trips: c._count.trips,
        buses: c._count.buses
      }))
    }
  }
}
