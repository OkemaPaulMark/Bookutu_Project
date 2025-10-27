# Bookutu - Bus Booking Platform

A comprehensive multi-tenant bus booking platform built with Django REST Framework, designed for both web dashboards and mobile applications (Flutter).

## Features

### 🚌 Core Functionality
- **Multi-tenant Architecture** - Separate data isolation for different bus companies
- **Three User Types** - Passengers, Company Staff, Super Admin
- **Direct Booking System** - Company staff can book on behalf of passengers
- **Mobile-First API** - Optimized endpoints for Flutter mobile app
- **Real-time Seat Management** - Live seat availability and selection
- **Payment Integration** - Multiple payment methods support

### 📱 Mobile API Features
- JWT Authentication with refresh tokens
- Trip search with filters (date, route, bus type)
- Visual seat selection and booking
- Booking history and management
- User profile management
- Push notification support
- QR code ticket generation

### 🏢 Company Dashboard
- Fleet management (buses, routes, schedules)
- Booking management and passenger manifest
- Direct booking interface for walk-in customers
- Financial reports and earnings tracking
- Trip analytics and performance metrics

### 👑 Super Admin Dashboard
- Platform overview and analytics
- Company verification and management
- User management across all companies
- Financial oversight and commission tracking
- System settings and announcements

## Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL with multi-tenant data isolation
- **Authentication**: JWT tokens with refresh mechanism
- **Task Queue**: Celery with Redis
- **API Documentation**: OpenAPI 3.0 with Swagger UI
- **Mobile Ready**: CORS configured for Flutter integration

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis (for Celery tasks)

### Installation

1. **Clone and Setup**
\`\`\`bash
git clone <repository-url>
cd bookutu-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

2. **Environment Configuration**
\`\`\`bash
cp .env.example .env
# Edit .env with your database and other settings
\`\`\`

3. **Database Setup**
\`\`\`bash
# Create PostgreSQL database
createdb bookutu

# Run setup script
python scripts/setup_database.py
\`\`\`

4. **Start Development Server**
\`\`\`bash
python manage.py runserver
\`\`\`

5. **Start Celery Worker** (in another terminal)
\`\`\`bash
celery -A bookutu worker -l info
\`\`\`

## API Documentation

Visit `http://localhost:8000/api/docs/` for interactive API documentation.

### Key Endpoints

#### Mobile API (`/api/mobile/`)
- `POST /auth/login/` - User authentication
- `POST /auth/register/` - User registration
- `POST /trips/search/` - Search available trips
- `GET /trips/{id}/` - Trip details with seat map
- `POST /bookings/create/` - Create new booking
- `GET /bookings/` - User's booking history

#### Company Dashboard (`/api/v1/`)
- `GET /companies/dashboard/` - Company dashboard data
- `POST /companies/buses/` - Add new bus
- `POST /trips/` - Create new trip
- `GET /bookings/manifest/{trip_id}/` - Passenger manifest

#### Super Admin (`/super-admin/`)
- `GET /dashboard/` - Platform overview
- `GET /companies/` - All companies management
- `POST /companies/{id}/verify/` - Verify company
- `GET /analytics/` - Platform analytics

## Database Schema

### Core Models
- **User** - Custom user model with role-based access
- **Company** - Bus company information and settings
- **Bus** - Fleet management with seat configurations
- **Route** - Travel routes between cities
- **Trip** - Scheduled trips with pricing
- **Booking** - Passenger bookings with seat assignments
- **Payment** - Payment tracking and processing

### Multi-Tenant Security
- Tenant middleware ensures data isolation
- Role-based permissions for all endpoints
- Company-specific data filtering
- Audit logging for sensitive operations

## Mobile App Integration

### Flutter Setup
The API is designed for seamless Flutter integration:

\`\`\`dart
// Example API configuration
const String baseUrl = 'http://your-domain.com/api/mobile';

// Authentication headers
Map<String, String> headers = {
  'Authorization': 'Bearer $accessToken',
  'Content-Type': 'application/json',
};
\`\`\`

### Key Mobile Features
- **Trip Search**: Real-time availability checking
- **Seat Selection**: Visual seat map interface
- **Booking Flow**: Multi-step booking process
- **Payment Integration**: Multiple payment gateways
- **Offline Support**: Cached data for offline viewing
- **Push Notifications**: Booking confirmations and updates

## Deployment

### Production Checklist
- [ ] Update `SECRET_KEY` and `DEBUG=False`
- [ ] Configure production database
- [ ] Set up Redis for Celery
- [ ] Configure email settings (SMTP)
- [ ] Set up SMS gateway for notifications
- [ ] Configure payment gateway credentials
- [ ] Set up SSL certificates
- [ ] Configure static file serving
- [ ] Set up monitoring and logging

### Docker Deployment
\`\`\`bash
# Build and run with Docker Compose
docker-compose up -d
\`\`\`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@bookutu.com
- Documentation: [API Docs](http://localhost:8000/api/docs/)
- Issues: GitHub Issues

---

**Built with ❤️ for the African transport industry**

## Group Integration (Compatibility Layer)

The group project [`Bookutu_Project`](https://github.com/OkemaPaulMark/Bookutu_Project) is vendored at `external/Bookutu_Project/` using a git subtree. We do NOT adopt its models/migrations/settings. Instead, we port compatible API shapes under `api/group-compat/` backed by this project's models and permissions.

### Mounted Compatibility Endpoints

- `GET /api/group-compat/companies/`
- `GET /api/group-compat/buses/`
- `GET /api/group-compat/routes/`
- `GET /api/group-compat/trips/`
- `POST /api/group-compat/trips/{id}/book/` (fields: `seat_number`, `passenger_name`, `passenger_phone`, optional `payment_method`, `payment_status`, `amount_paid`)
- `GET /api/group-compat/bookings/` and `GET /api/group-compat/bookings/{id}/`

### Field Mapping Highlights

- Group `BusCompany` → `companies.Company` (uses `id` in responses)
- Group `Bus.number_plate` ↔ `companies.Bus.license_plate`
- Group `Bus.is_active` ↔ `companies.Bus.status == 'ACTIVE'`
- Group `Route.start_location/end_location` ↔ `trips.Route.origin_city/destination_city`
- Group `Trip.departure_time/arrival_time` ↔ `trips.Trip.departure_date+departure_time/arrival_time`
- Group `Booking.seat_number` ↔ `companies.BusSeat.seat_number`
- Group payment fields map to `payments.Payment` and auto-confirm on completed payments

### Tenancy & Auth

- Endpoints require authentication and honor tenant scoping via `accounts.middleware.TenantMiddleware`.
- Company staff see their company data; other users see only their own bookings.

### Merge Workflow

1. Keep `integrate/group-project` as the working branch for compatibility work.
2. To update the vendored code: `git subtree pull --prefix=external/Bookutu_Project group master --squash`.
3. Port additional endpoints by adapting views/serializers in `group_compat` to local models.

