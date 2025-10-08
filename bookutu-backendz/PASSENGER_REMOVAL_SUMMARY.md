# Passenger Functionality Removal Summary

## Overview
The Bookutu bus booking platform has been updated to support only two user types:
- **Super Admin**: Platform administrators with full system access
- **Company Staff**: Bus company employees who manage their company's operations

## Removed Components

### 1. Templates
- ❌ `templates/home/passenger_home.html` - Passenger dashboard template

### 2. User Model Updates
- ❌ Removed `PASSENGER` from `USER_TYPE_CHOICES`
- ❌ Removed `is_passenger()` method
- ✅ Updated default user type to `COMPANY_STAFF`
- ✅ Updated validation logic to exclude passenger references

### 3. Admin Dashboard Updates
- ❌ Removed "Passengers" navigation menu item
- ✅ Updated passenger statistics to show "Company Staff" instead
- ❌ Removed all `/admin/users/` URL references

### 4. Views and Forms
- ❌ Removed `web_register()` function for passenger registration
- ❌ Removed `PassengerRegistrationForm` class
- ❌ Removed `UserRegistrationView` API endpoint
- ❌ Removed passenger dashboard data from `user_dashboard_data()`

### 5. Permissions
- ❌ Removed `IsPassenger` permission class
- ✅ Kept `IsCompanyStaff` and `IsSuperAdmin` permissions

### 6. API Endpoints
- ❌ Commented out entire mobile API (`/api/mobile/`) since it was designed for passenger use
- ✅ Kept company and admin API endpoints

### 7. URL Configuration
- ❌ Removed `/admin/users/` URL pattern
- ❌ Disabled mobile API routes

## Retained Functionality

### Booking System
- ✅ Booking models remain intact for company staff to create bookings on behalf of customers
- ✅ Direct booking functionality for walk-in customers
- ✅ Company staff can manage all bookings for their company

### User Management
- ✅ Super admins can manage company staff accounts
- ✅ Company staff accounts linked to their respective companies
- ✅ Authentication and session management for both user types

### Dashboard Access
- ✅ Company dashboard at `/company/`
- ✅ Super admin dashboard at `/admin/`
- ✅ Landing page with links to both dashboards

## System Architecture
The system now operates as a B2B platform where:
1. **Bus companies** register and manage their operations through company staff accounts
2. **Super admins** oversee the entire platform and manage companies
3. **Bookings** are created by company staff for customers (no direct customer accounts)
4. **Mobile API** is disabled since there are no passenger users

## Migration Notes
- Existing passenger data in the database will remain but cannot be accessed through the UI
- Company staff can continue to create bookings using passenger information stored in booking records
- The system maintains data integrity while removing passenger-facing functionality