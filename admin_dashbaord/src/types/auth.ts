export type UserRole = 'SUPER_ADMIN' | 'COMPANY_STAFF'

export interface AuthUser {
  name: string
  email: string
  role: UserRole
}
