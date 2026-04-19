import 'express'

declare global {
  namespace Express {
    interface Request {
      logContext?: {
        method: string
        path: string
        timestamp: string
      }
      authUser?: {
        id: string
        userType: 'COMPANY_STAFF' | 'SUPER_ADMIN' | 'PASSENGER'
        companyId?: string | null
      }
    }
  }
}

export {}
