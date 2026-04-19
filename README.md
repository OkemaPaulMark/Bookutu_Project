# Bookutu Bus Booking and Management Project

This repository contains the core codebase for the Bookutu Bus Booking and Management platform, a comprehensive bus booking and management system. The project is organized into several main components:

## Main Components

- **express-backend/**: The main backend API, built with Node.js, Express, TypeScript, and Prisma ORM. It provides authentication, company management, fleet, trips, bookings, payments, and notifications APIs.
- **admin_dashbaord/**: The web-based admin dashboard for managing companies, trips, bookings, and more. Built with React, TypeScript, Vite, and Tailwind CSS. It connects to the backend for real-time management and analytics.
- **bus_app/**: The frontend/mobile application (originally Flutter).

## Features

- User authentication and registration
- Company and fleet management
- Trip scheduling and manifest
- Seat booking and payment processing
- Notifications and announcements
- Modular, layered architecture for maintainability

## Getting Started

1. **Backend Setup**
   - Navigate to `express-backend/`
   - Install dependencies: `npm install`
   - Set up your `.env` file with database and JWT secrets
   - Run database migrations: `npx prisma migrate deploy`
   - Start the server: `npm run dev`

2. **Admin Dashboard Setup**
   - Navigate to `admin_dashbaord/`
   - Install dependencies: `npm install`
   - Start the development server: `npm run dev`

3. **Frontend/Mobile App Setup**
   - Navigate to `bus_app/`
   - Follow the Flutter setup instructions in the `README.md` inside `bus_app/`

## Notes

- All legacy Django and Firebase code has been removed or migrated.
- The backend is fully TypeScript and Prisma-based.
- For any issues, see the module-specific README files or contact the maintainers.

---

**Bookutu StartUp** — Modern Bus Booking Platform

# Bookutu Bus Booking and Management System
