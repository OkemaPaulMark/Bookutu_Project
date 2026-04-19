import express, { type Request, type Response } from 'express'
import cors from 'cors'
import helmet from 'helmet'
import morgan from 'morgan'
import { apiRoutes } from './routes/index.js'
import { errorHandler, notFoundHandler } from './middlewares/error.middleware.js'
import { requestLogger } from './middlewares/requestLogger.middleware.js'

export const app = express()

app.use(helmet())
app.use(cors({ origin: true, credentials: true }))
app.use(express.json({ limit: '2mb' }))
app.use(express.urlencoded({ extended: true }))
app.use(morgan('dev'))
app.use(requestLogger)

app.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok', service: 'bookutu-express-backend' })
})

app.use('/api/v1', apiRoutes)

app.use(notFoundHandler)
app.use(errorHandler)
