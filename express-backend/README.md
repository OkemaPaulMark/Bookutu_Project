# Bookutu Express Backend

Node.js + Express.js backend scaffold for the Bookutu migration.

## Stack

- Express
- Prisma
- PostgreSQL
- TypeScript
- Layered architecture: controllers, services, repositories, middleware, utils, routes

## Scripts

- `npm run dev`
- `npm run build`
- `npm run start`
- `npm run prisma:generate`
- `npm run prisma:migrate`

## Structure

- `src/app.ts`
- `src/server.ts`
- `src/config/`
- `src/middlewares/`
- `src/utils/`
- `src/modules/`
- `prisma/schema.prisma`

### Module Layering Pattern

Each domain module follows this internal layered flow:

- `*.routes.ts` -> receives HTTP requests and binds controller handlers
- `*.controller.ts` -> parses request/response concerns only
- `*.service.ts` -> applies business rules and orchestration
- `*.repository.ts` -> owns Prisma data access

Example modules:

- `src/modules/auth/`
- `src/modules/companies/`
- `src/modules/fleet/`
- `src/modules/trips/`
- `src/modules/bookings/`
- `src/modules/payments/`
- `src/modules/notifications/`
