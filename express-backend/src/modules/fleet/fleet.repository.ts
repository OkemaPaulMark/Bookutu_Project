import { prisma } from '../../config/prisma.js'

export const fleetRepository = {
  async findBuses(companyId?: string | null) {
    return prisma.bus.findMany({
      where: companyId ? { companyId } : undefined,
      include: {
        company: { select: { id: true, name: true } },
        _count: { select: { seats: true, trips: true } }
      },
      orderBy: { createdAt: 'desc' }
    })
  },

  async findById(id: string) {
    return prisma.bus.findUnique({
      where: { id },
      include: {
        company: { select: { id: true, name: true } },
        seats: { orderBy: [{ rowNumber: 'asc' }, { seatNumber: 'asc' }] }
      }
    })
  },

  async create(data: {
    companyId: string
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
  }) {
    return prisma.bus.create({ data })
  },

  async createSeats(busId: string, totalSeats: number) {
    const seatPositions = ['LEFT_WINDOW', 'LEFT_AISLE', 'RIGHT_AISLE', 'RIGHT_WINDOW']
    const seatLetters = ['A', 'B', 'C', 'D']
    const seatCount = Math.floor(totalSeats / 4) * 4
    const rows = seatCount / 4

    if (rows <= 0) return

    await prisma.busSeat.createMany({
      data: Array.from({ length: rows }).flatMap((_, rowIndex) => {
        const rowNumber = rowIndex + 1
        return seatLetters.map((letter, index) => ({
          busId,
          seatNumber: `${rowNumber}${letter}`,
          rowNumber,
          seatPosition: seatPositions[index],
          seatType: 'REGULAR',
          isWindow: index === 0 || index === 3,
          isAisle: index === 1 || index === 2,
          hasExtraLegroom: false,
          priceMultiplier: 1
        }))
      }),
      skipDuplicates: true
    })
  },

  async update(id: string, data: Partial<{
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
  }>) {
    return prisma.bus.update({ where: { id }, data })
  },

  // Routes
  async findRoutes(companyId?: string | null) {
    return prisma.route.findMany({
      where: companyId ? { companyId } : undefined,
      include: { company: { select: { id: true, name: true } } },
      orderBy: { createdAt: 'desc' }
    })
  },

  async findRouteById(id: string) {
    return prisma.route.findUnique({
      where: { id },
      include: { company: { select: { id: true, name: true } } }
    })
  },

  async createRoute(data: {
    companyId: string
    name: string
    originCity: string
    originTerminal: string
    destinationCity: string
    destinationTerminal: string
    distanceKm: number
    estimatedDurationHours: number
    baseFare: number
    intermediateStops?: object
  }) {
    return prisma.route.create({ data })
  },

  async updateRoute(id: string, data: Partial<{
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
  }>) {
    return prisma.route.update({ where: { id }, data })
  },

  // Drivers
  async findDrivers(companyId?: string | null) {
    return prisma.driver.findMany({
      where: companyId ? { companyId } : undefined,
      include: { company: { select: { id: true, name: true } } },
      orderBy: { createdAt: 'desc' }
    })
  },

  async findDriverById(id: string) {
    return prisma.driver.findUnique({
      where: { id },
      include: { company: { select: { id: true, name: true } } }
    })
  },

  async createDriver(data: {
    companyId: string
    firstName: string
    lastName: string
    phoneNumber: string
    email?: string
    licenseNumber: string
    licenseExpiryDate: Date
    dateOfBirth: Date
    employeeId?: string
    hireDate: Date
  }) {
    return prisma.driver.create({ data })
  },

  async updateDriver(id: string, data: Partial<{
    firstName: string
    lastName: string
    phoneNumber: string
    email: string
    licenseNumber: string
    licenseExpiryDate: Date
    status: string
  }>) {
    return prisma.driver.update({ where: { id }, data })
  }
}
