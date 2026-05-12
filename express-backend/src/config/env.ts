import dotenv from 'dotenv'
import { z } from 'zod'

dotenv.config()

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().default(4000),
  DATABASE_URL: z.string().min(1),
  JWT_ACCESS_SECRET: z.string().min(1),
  JWT_REFRESH_SECRET: z.string().min(1),
  CORS_ORIGIN: z.string().optional(),
  DASHBOARD_BASE_URL: z.string().url().optional(),
  ORGANIZER_DASHBOARD_URL: z.string().url().default('http://localhost:5174/login'),
  EMAIL_USER: z.string().email().optional(),
  EMAIL_PASSWORD: z.string().min(1).optional(),
  EMAIL_FROM_ADDRESS: z.string().email().optional(),
  RESEND_API_KEY: z.string().optional()
})

export const env = envSchema.parse(process.env)
