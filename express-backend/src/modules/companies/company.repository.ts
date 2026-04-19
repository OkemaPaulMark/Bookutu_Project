import { prisma } from '../../config/prisma.js'

export const companyRepository = {
  async findAll(params: { search?: string, status?: 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'INACTIVE' }) {
    return prisma.company.findMany({
      where: {
        status: params.status,
        OR: params.search
          ? [
              { name: { contains: params.search, mode: 'insensitive' } },
              { email: { contains: params.search, mode: 'insensitive' } },
              { phoneNumber: { contains: params.search, mode: 'insensitive' } }
            ]
          : undefined
      },
      orderBy: { createdAt: 'desc' }
    })
  },

  async findById(id: string) {
    return prisma.company.findUnique({
      where: { id },
      include: {
        _count: {
          select: {
            buses: true,
            routes: true,
            trips: true,
            bookings: true
          }
        }
      }
    })
  },

  async findBySlug(slug: string) {
    return prisma.company.findUnique({ where: { slug } })
  },

  async create(data: {
    name: string
    slug: string
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
    return prisma.company.create({
      data: {
        ...data,
        commissionRate: data.commissionRate ?? 10,
        country: data.country ?? 'Uganda'
      }
    })
  },

  async update(id: string, data: Partial<{
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
  }>) {
    return prisma.company.update({ where: { id }, data })
  }
}
