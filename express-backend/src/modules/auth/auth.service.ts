import { authRepository } from './auth.repository.js'
import { AppError } from '../../utils/AppError.js'
import { signAccessToken, signRefreshToken, verifyRefreshToken } from '../../utils/token.js'
import bcrypt from 'bcryptjs'
import { prisma } from '../../config/prisma.js'

export const authService = {
  async login(payload: { email: string, password: string }) {
    const user = await authRepository.findUserByEmail(payload.email)

    if (!user || !user.isActive) {
      throw new AppError(401, 'Invalid email or password')
    }

    const isValidPassword = await bcrypt.compare(payload.password, user.passwordHash)
    if (!isValidPassword) {
      throw new AppError(401, 'Invalid email or password')
    }

    const tokenPayload = {
      sub: user.id,
      userType: user.userType,
      companyId: user.companyId
    }

    return {
      access: signAccessToken(tokenPayload),
      refresh: signRefreshToken(tokenPayload),
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        phoneNumber: user.phoneNumber,
        userType: user.userType,
        companyId: user.companyId,
        companyName: user.company?.name ?? null,
        isVerified: user.isVerified
      }
    }
  },

  async refresh(refreshToken: string) {
    const payload = verifyRefreshToken(refreshToken)
    const user = await authRepository.findUserById(payload.sub)

    if (!user || !user.isActive) {
      throw new AppError(401, 'Invalid refresh token')
    }

    return {
      access: signAccessToken({
        sub: user.id,
        userType: user.userType,
        companyId: user.companyId
      }),
      refresh: signRefreshToken({
        sub: user.id,
        userType: user.userType,
        companyId: user.companyId
      })
    }
  },

  async me(userId: string) {
    const user = await authRepository.findUserById(userId)
    if (!user) {
      throw new AppError(404, 'User not found')
    }

    return {
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      phoneNumber: user.phoneNumber,
      userType: user.userType,
      companyId: user.companyId,
      companyName: user.company?.name ?? null,
      isVerified: user.isVerified,
      createdAt: user.createdAt
    }
  },

  async registerPassenger(payload: {
    email: string
    username?: string
    firstName?: string
    lastName?: string
    phoneNumber?: string
    password: string
  }) {
    const existing = await authRepository.findUserByEmail(payload.email)
    if (existing) {
      throw new AppError(409, 'Email already exists')
    }

    const passwordHash = await bcrypt.hash(payload.password, 10)
    const user = await authRepository.createUser({
      email: payload.email,
      username: payload.username,
      firstName: payload.firstName,
      lastName: payload.lastName,
      phoneNumber: payload.phoneNumber,
      passwordHash,
      userType: 'PASSENGER',
      isVerified: false
    })

    return {
      id: user.id,
      email: user.email,
      userType: user.userType
    }
  },

  async registerCompanyStaff(payload: {
    email: string
    firstName?: string
    lastName?: string
    phoneNumber?: string
    password: string
    companyId: string
  }) {
    const existing = await authRepository.findUserByEmail(payload.email)
    if (existing) {
      throw new AppError(409, 'Email already exists')
    }

    const company = await prisma.company.findUnique({ where: { id: payload.companyId } })
    if (!company) {
      throw new AppError(400, 'Invalid company')
    }

    const passwordHash = await bcrypt.hash(payload.password, 10)
    const user = await authRepository.createUser({
      email: payload.email,
      firstName: payload.firstName,
      lastName: payload.lastName,
      phoneNumber: payload.phoneNumber,
      passwordHash,
      userType: 'COMPANY_STAFF',
      companyId: payload.companyId,
      isVerified: true
    })

    return {
      id: user.id,
      email: user.email,
      userType: user.userType,
      companyId: user.companyId
    }
  }
}
