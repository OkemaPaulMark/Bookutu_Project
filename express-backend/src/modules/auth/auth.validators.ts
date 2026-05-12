import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export const registerPassengerSchema = z.object({
  email: z.string().email(),
  username: z.string().trim().min(3).max(32).optional(),
  firstName: z.string().trim().min(2).max(50),
  lastName: z.string().trim().min(2).max(50),
  phoneNumber: z.string().trim().min(7).max(20).optional(),
  password: z.string().min(8),
  confirmPassword: z.string().min(8)
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
})

export const inviteCompanyAdminSchema = z.object({
  email: z.string().email(),
  companyId: z.string().min(1),
  firstName: z.string().trim().min(2).max(50).optional(),
  lastName: z.string().trim().min(2).max(50).optional(),
  phoneNumber: z.string().trim().min(7).max(20).optional()
})

export const setPasswordSchema = z.object({
  token: z.string().min(20),
  firstName: z.string().trim().min(2).max(50),
  lastName: z.string().trim().min(2).max(50),
  phoneNumber: z.string().trim().min(7).max(20).optional(),
  password: z.string().min(8),
  confirmPassword: z.string().min(8)
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
})

export const bootstrapSuperAdminSchema = z.object({
  email: z.string().email(),
  firstName: z.string().trim().min(2).max(50),
  lastName: z.string().trim().min(2).max(50),
  phoneNumber: z.string().trim().min(7).max(20).optional(),
  password: z.string().min(8),
  confirmPassword: z.string().min(8)
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
})
