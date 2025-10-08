-- Seed data for Bookutu platform
-- This script adds initial data for testing and development

-- Insert sample routes (major Ugandan cities)
INSERT INTO trips_route (origin, destination, distance_km, estimated_duration, created_at, updated_at) VALUES
('Kampala', 'Mbarara', 290, '04:30:00', NOW(), NOW()),
('Kampala', 'Gulu', 340, '05:00:00', NOW(), NOW()),
('Kampala', 'Mbale', 245, '04:00:00', NOW(), NOW()),
('Kampala', 'Fort Portal', 320, '05:30:00', NOW(), NOW()),
('Kampala', 'Jinja', 87, '01:30:00', NOW(), NOW()),
('Mbarara', 'Kasese', 180, '03:00:00', NOW(), NOW()),
('Gulu', 'Arua', 120, '02:00:00', NOW(), NOW()),
('Mbale', 'Soroti', 95, '01:45:00', NOW(), NOW()),
('Kampala', 'Masaka', 135, '02:30:00', NOW(), NOW()),
('Kampala', 'Lira', 350, '05:15:00', NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Insert sample super admin user
INSERT INTO accounts_user (
    email, password, first_name, last_name, phone_number, 
    user_type, is_active, is_staff, is_superuser, date_joined
) VALUES (
    'admin@bookutu.com', 
    'pbkdf2_sha256$600000$placeholder$hash', -- Change this password!
    'Super', 
    'Admin', 
    '+256700000000', 
    'SUPER_ADMIN', 
    true, 
    true, 
    true, 
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Insert sample bus companies
INSERT INTO companies_company (
    name, email, phone_number, address, license_number, 
    status, is_verified, rating, created_at, updated_at
) VALUES
('Swift Safaris', 'info@swiftsafaris.ug', '+256701234567', 'Kampala, Uganda', 'SS001', 'ACTIVE', true, 4.5, NOW(), NOW()),
('Post Bus', 'contact@postbus.ug', '+256702345678', 'Kampala, Uganda', 'PB002', 'ACTIVE', true, 4.2, NOW(), NOW()),
('Jaguar Executive', 'info@jaguarexec.ug', '+256703456789', 'Kampala, Uganda', 'JE003', 'ACTIVE', true, 4.7, NOW(), NOW()),
('Link Bus', 'hello@linkbus.ug', '+256704567890', 'Kampala, Uganda', 'LB004', 'ACTIVE', true, 4.0, NOW(), NOW()),
('Gateway Bus', 'info@gatewaybus.ug', '+256705678901', 'Kampala, Uganda', 'GB005', 'ACTIVE', true, 4.3, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Insert sample company staff users
INSERT INTO accounts_user (
    email, password, first_name, last_name, phone_number, 
    user_type, is_active, company_id, date_joined
) VALUES 
('manager@swiftsafaris.ug', 'pbkdf2_sha256$600000$placeholder$hash', 'John', 'Manager', '+256711111111', 'COMPANY_STAFF', true, 1, NOW()),
('staff@postbus.ug', 'pbkdf2_sha256$600000$placeholder$hash', 'Jane', 'Staff', '+256722222222', 'COMPANY_STAFF', true, 2, NOW()),
('admin@jaguarexec.ug', 'pbkdf2_sha256$placeholder$hash', 'Mike', 'Admin', '+256733333333', 'COMPANY_STAFF', true, 3, NOW())
ON CONFLICT (email) DO NOTHING;

-- Insert sample passenger
INSERT INTO accounts_user (
    email, password, first_name, last_name, phone_number, 
    user_type, is_active, date_joined
) VALUES (
    'passenger@example.com', 
    'pbkdf2_sha256$600000$placeholder$hash', 
    'Test', 
    'Passenger', 
    '+256788888888', 
    'PASSENGER', 
    true, 
    NOW()
) ON CONFLICT (email) DO NOTHING;

COMMIT;

-- Note: Remember to update passwords using Django's management commands:
-- python manage.py changepassword admin@bookutu.com
-- python manage.py changepassword manager@swiftsafaris.ug
