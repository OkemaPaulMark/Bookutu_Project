import jwt from 'jsonwebtoken'
import { env } from '../config/env.js'

type TokenPayload = {
  sub: string
  userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
  companyId?: string | null
}

// In-memory blacklist — swap for Redis in production
const blacklistedTokens = new Set<string>()

export function blacklistToken(token: string) {
  blacklistedTokens.add(token)
}

export function isTokenBlacklisted(token: string) {
  return blacklistedTokens.has(token)
}

export function signAccessToken(payload: TokenPayload): string {
  return jwt.sign(payload, env.JWT_ACCESS_SECRET, { expiresIn: '24h' })
}

export function signRefreshToken(payload: TokenPayload): string {
  return jwt.sign(payload, env.JWT_REFRESH_SECRET, { expiresIn: '7d' })
}

export function verifyAccessToken(token: string): TokenPayload {
  return jwt.verify(token, env.JWT_ACCESS_SECRET) as TokenPayload
}

export function verifyRefreshToken(token: string): TokenPayload {
  if (isTokenBlacklisted(token)) {
    throw new Error('Token has been revoked')
  }
  return jwt.verify(token, env.JWT_REFRESH_SECRET) as TokenPayload
}
