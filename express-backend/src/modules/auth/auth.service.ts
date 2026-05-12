import { authRepository } from './auth.repository.js'
import { AppError } from '../../utils/AppError.js'
import { signAccessToken, signRefreshToken, verifyRefreshToken } from '../../utils/token.js'
import bcrypt from 'bcryptjs'
import { prisma } from '../../config/prisma.js'
import { env } from '../../config/env.js'
import { emailService } from '../../services/email.service.js'
import { createHash, randomBytes, randomUUID } from 'node:crypto'

type UserRecord = Awaited<ReturnType<typeof authRepository.findUserById>>

function buildTokenPayload(user: NonNullable<UserRecord>) {
  return {
    sub: user.id,
    userType: user.userType,
    companyId: user.companyId
  }
}

function serializeUser(user: NonNullable<UserRecord>) {
  return {
    id: user.id,
    email: user.email,
    username: user.username,
    firstName: user.firstName,
    lastName: user.lastName,
    phoneNumber: user.phoneNumber,
    userType: user.userType,
    companyId: user.companyId,
    companyName: user.company?.name ?? null,
    companyStatus: user.company?.status ?? null,
    isVerified: user.isVerified,
    createdAt: user.createdAt
  }
}

function createPasswordSetupToken() {
  const rawToken = randomBytes(32).toString('hex')
  const tokenHash = createHash('sha256').update(rawToken).digest('hex')
  const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24)

  return {
    rawToken,
    tokenHash,
    expiresAt
  }
}

export const authService = {
  async login(payload: { email: string, password: string }) {
    const user = await authRepository.findUserByEmail(payload.email)

    if (!user || !user.isActive) {
      throw new AppError(401, 'Invalid email or password')
    }

    if (!user.isVerified) {
      throw new AppError(403, 'Account setup is not complete yet. Please use the password setup link from your email.')
    }

    const isValidPassword = await bcrypt.compare(payload.password, user.passwordHash)
    if (!isValidPassword) {
      throw new AppError(401, 'Invalid email or password')
    }

    const tokenPayload = buildTokenPayload(user)

    return {
      access: signAccessToken(tokenPayload),
      refresh: signRefreshToken(tokenPayload),
      user: serializeUser(user)
    }
  },

  async refresh(refreshToken: string) {
    const payload = verifyRefreshToken(refreshToken)
    const user = await authRepository.findUserById(payload.sub)

    if (!user || !user.isActive) {
      throw new AppError(401, 'Invalid refresh token')
    }

    return {
      access: signAccessToken(buildTokenPayload(user)),
      refresh: signRefreshToken(buildTokenPayload(user))
    }
  },

  async me(userId: string) {
    const user = await authRepository.findUserById(userId)
    if (!user) {
      throw new AppError(404, 'User not found')
    }

    return serializeUser(user)
  },

  async registerPassenger(payload: {
    email: string
    username?: string
    firstName: string
    lastName: string
    phoneNumber?: string
    password: string
    confirmPassword: string
  }) {
    const existing = await authRepository.findUserByEmail(payload.email)
    if (existing) {
      throw new AppError(409, 'Email already exists')
    }

    if (payload.username) {
      const existingUsername = await authRepository.findUserByUsername(payload.username)
      if (existingUsername) {
        throw new AppError(409, 'Username already exists')
      }
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
      isVerified: true
    })

    const tokenPayload = buildTokenPayload({
      ...user,
      company: null
    })

    return {
      access: signAccessToken(tokenPayload),
      refresh: signRefreshToken(tokenPayload),
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        firstName: user.firstName,
        lastName: user.lastName,
        phoneNumber: user.phoneNumber,
        userType: user.userType,
        companyId: user.companyId,
        companyName: null,
        companyStatus: null,
        isVerified: user.isVerified,
        createdAt: user.createdAt
      }
    }
  },

  async inviteCompanyAdmin(payload: {
    email: string
    firstName?: string
    lastName?: string
    phoneNumber?: string
    companyId: string
  }) {
    const company = await prisma.company.findUnique({ where: { id: payload.companyId } })
    if (!company) {
      throw new AppError(400, 'Invalid company')
    }

    const existing = await authRepository.findUserByEmail(payload.email)
    const { rawToken, tokenHash, expiresAt } = createPasswordSetupToken()
    const placeholderPasswordHash = await bcrypt.hash(randomUUID(), 10)
    const invitedAt = new Date()

    let user: NonNullable<UserRecord>

    if (existing) {
      if (existing.userType !== 'COMPANY_STAFF') {
        throw new AppError(409, 'This email is already used by another Bookutu account')
      }

      if (existing.isVerified) {
        throw new AppError(409, 'This company admin already has an active account')
      }

      user = await authRepository.updateUser(existing.id, {
        firstName: payload.firstName ?? existing.firstName ?? null,
        lastName: payload.lastName ?? existing.lastName ?? null,
        phoneNumber: payload.phoneNumber ?? existing.phoneNumber ?? null,
        companyId: payload.companyId,
        isActive: true,
        passwordHash: placeholderPasswordHash,
        passwordSetupTokenHash: tokenHash,
        passwordSetupTokenExpiresAt: expiresAt,
        invitedAt
      })
    } else {
      user = await authRepository.createUser({
        email: payload.email,
        firstName: payload.firstName,
        lastName: payload.lastName,
        phoneNumber: payload.phoneNumber,
        passwordHash: placeholderPasswordHash,
        userType: 'COMPANY_STAFF',
        companyId: payload.companyId,
        isActive: true,
        isVerified: false,
        passwordSetupTokenHash: tokenHash,
        passwordSetupTokenExpiresAt: expiresAt,
        invitedAt
      })
    }

    const setupBaseUrl = env.DASHBOARD_BASE_URL ?? env.ORGANIZER_DASHBOARD_URL.replace(/\/login\/?$/, '')
    const setupUrl = `${setupBaseUrl}/set-password?token=${rawToken}`
    const delivery = await emailService.sendCompanyAdminInvite({
      to: payload.email,
      companyName: company.name,
      setupUrl
    })

    return {
      message: 'Company admin invite created successfully',
      invite: {
        email: user.email,
        companyId: company.id,
        companyName: company.name,
        expiresAt,
        deliveryMode: delivery.mode
      },
      setupUrl: env.NODE_ENV === 'production' ? undefined : setupUrl
    }
  },

  async getPasswordSetupDetails(token: string) {
    const tokenHash = createHash('sha256').update(token).digest('hex')
    const user = await authRepository.findUserByPasswordSetupTokenHash(tokenHash)

    if (!user || !user.passwordSetupTokenExpiresAt || user.passwordSetupTokenExpiresAt.getTime() < Date.now()) {
      throw new AppError(400, 'This password setup link is invalid or has expired')
    }

    return {
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      phoneNumber: user.phoneNumber,
      companyName: user.company?.name ?? null
    }
  },

  async setPassword(payload: {
    token: string
    firstName: string
    lastName: string
    phoneNumber?: string
    password: string
    confirmPassword: string
  }) {
    const tokenHash = createHash('sha256').update(payload.token).digest('hex')
    const user = await authRepository.findUserByPasswordSetupTokenHash(tokenHash)

    if (!user || !user.passwordSetupTokenExpiresAt || user.passwordSetupTokenExpiresAt.getTime() < Date.now()) {
      throw new AppError(400, 'This password setup link is invalid or has expired')
    }

    const passwordHash = await bcrypt.hash(payload.password, 10)

    const updatedUser = await authRepository.updateUser(user.id, {
      firstName: payload.firstName,
      lastName: payload.lastName,
      phoneNumber: payload.phoneNumber ?? null,
      passwordHash,
      isVerified: true,
      passwordSetupTokenHash: null,
      passwordSetupTokenExpiresAt: null
    })

    const hydratedUser = await authRepository.findUserById(updatedUser.id)
    if (!hydratedUser) {
      throw new AppError(404, 'User not found after password setup')
    }

    const tokenPayload = buildTokenPayload(hydratedUser)

    return {
      message: 'Password set successfully',
      access: signAccessToken(tokenPayload),
      refresh: signRefreshToken(tokenPayload),
      user: serializeUser(hydratedUser)
    }
  },

  async bootstrapSuperAdmin(payload: {
    email: string
    firstName: string
    lastName: string
    phoneNumber?: string
    password: string
    confirmPassword: string
  }) {
    const superAdminCount = await authRepository.countSuperAdmins()
    if (superAdminCount > 0) {
      throw new AppError(409, 'A Bookutu super admin already exists')
    }

    const existing = await authRepository.findUserByEmail(payload.email)
    if (existing) {
      throw new AppError(409, 'Email already exists')
    }

    const passwordHash = await bcrypt.hash(payload.password, 10)
    const user = await authRepository.createUser({
      email: payload.email,
      firstName: payload.firstName,
      lastName: payload.lastName,
      phoneNumber: payload.phoneNumber,
      passwordHash,
      userType: 'SUPER_ADMIN',
      isVerified: true
    })

    const tokenPayload = buildTokenPayload({
      ...user,
      company: null
    })

    return {
      message: 'Super admin created successfully',
      access: signAccessToken(tokenPayload),
      refresh: signRefreshToken(tokenPayload),
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        firstName: user.firstName,
        lastName: user.lastName,
        phoneNumber: user.phoneNumber,
        userType: user.userType,
        companyId: user.companyId,
        companyName: null,
        companyStatus: null,
        isVerified: user.isVerified,
        createdAt: user.createdAt
      }
    }
  }
}
