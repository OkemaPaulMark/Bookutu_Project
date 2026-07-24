# Bookutu Bus Booking and Management Project

This repository contains the core codebase for the Bookutu Bus Booking and Management platform, a comprehensive bus booking and management system. The project is organized into several main components:

## Main Components

- **django-backend/**: The main backend API, built with Django, Django REST Framework, and PostgreSQL. It provides authentication, company management, fleet, trips, bookings, payments, and notifications APIs.
- **admin_dashbaord/**: The web-based admin dashboard for managing companies, trips, bookings, and more. Built with React, TypeScript, Vite, and Tailwind CSS. It connects to the backend for real-time management and analytics.
- **bus_app/**: The frontend/mobile application (originally Flutter).

## Features

- User authentication and registration (JWT access/refresh tokens with rotation and blacklisting)
- Company and fleet management
- Trip scheduling and manifest
- Seat booking and payment processing
- Notifications and announcements
- Modular, layered architecture for maintainability

## Getting Started

1. **Backend Setup**
   - Navigate to `django-backend/`
   - Create/activate the virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`
   - Set up your `.env` file with database credentials and Django secret key
   - Run database migrations: `python manage.py migrate`
   - Start the server: `python manage.py runserver`

2. **Admin Dashboard Setup**
   - Navigate to `admin_dashbaord/`
   - Install dependencies: `npm install`
   - Start the development server: `npm run dev`

3. **Frontend/Mobile App Setup**
   - Navigate to `bus_app/`
   - Follow the Flutter setup instructions in the `README.md` inside `bus_app/`

## Notes

- The backend is fully Django and PostgreSQL-based.
- For any issues, see the module-specific README files or contact the maintainers.

---

**Bookutu StartUp** — Modern Bus Booking Platform

# Bookutu Bus Booking and Management System
