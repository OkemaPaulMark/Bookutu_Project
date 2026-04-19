-- Initial database setup for Bookutu bus booking platform
-- Run this script to create the initial database structure

-- Create database (run as superuser)
-- CREATE DATABASE bookutu;
-- CREATE USER bookutu_user WITH PASSWORD 'your_secure_password';
-- GRANT ALL PRIVILEGES ON DATABASE bookutu TO bookutu_user;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON accounts_user(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_phone ON accounts_user(phone_number);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_type ON accounts_user(user_type);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_status ON companies_company(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_verified ON companies_company(is_verified);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_date ON trips_trip(departure_date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_status ON trips_trip(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_company ON trips_trip(company_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_user ON bookings_booking(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_trip ON bookings_booking(trip_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_status ON bookings_booking(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_reference ON bookings_booking(booking_reference);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_seats_trip ON bookings_seat(trip_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_seats_available ON bookings_seat(is_available);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_booking ON payments_payment(booking_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_status ON payments_payment(status);

-- Create full-text search indexes for routes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_routes_origin_search ON trips_route USING gin(to_tsvector('english', origin));
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_routes_destination_search ON trips_route USING gin(to_tsvector('english', destination));

-- Create composite indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_route_date ON trips_trip(route_id, departure_date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_user_status ON bookings_booking(user_id, status);

COMMIT;
