export type UserRole = 'SUPER_ADMIN' | 'COMPANY_STAFF'

export interface AuthUser {
  id: string
  name: string
  email: string
  role: UserRole
  firstName?: string | null
  lastName?: string | null
  phoneNumber?: string | null
  companyId?: string | null
  companyName?: string | null
  companyStatus?: 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'INACTIVE' | null
  isVerified: boolean
}
