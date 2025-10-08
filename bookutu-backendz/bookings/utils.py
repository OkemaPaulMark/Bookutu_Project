from django.conf import settings
from django.utils import timezone
import requests
import json
from datetime import datetime


def generate_ticket(booking, format='digital'):
    """
    Generate ticket data for a booking
    """
    ticket_data = {
        'booking_reference': booking.booking_reference,
        'passenger_name': booking.passenger_name,
        'passenger_phone': booking.passenger_phone,
        'company_name': booking.company.name,
        'route': f"{booking.trip.route.origin_city} → {booking.trip.route.destination_city}",
        'origin_terminal': booking.trip.route.origin_terminal,
        'destination_terminal': booking.trip.route.destination_terminal,
        'departure_date': booking.trip.departure_date.strftime('%Y-%m-%d'),
        'departure_time': booking.trip.departure_time.strftime('%H:%M'),
        'arrival_time': booking.trip.arrival_time.strftime('%H:%M'),
        'seat_number': booking.seat.seat_number,
        'bus_registration': booking.trip.bus.registration_number,
        'driver_name': booking.trip.driver_name,
        'driver_phone': booking.trip.driver_phone,
        'total_amount': str(booking.total_amount),
        'booking_date': booking.created_at.strftime('%Y-%m-%d %H:%M'),
        'status': booking.status,
        'qr_code_data': f"BOOKUTU:{booking.booking_reference}:{booking.trip.id}:{booking.seat.seat_number}"
    }
    
    if format == 'print':
        # Add additional formatting for thermal printer
        ticket_data['print_format'] = {
            'header': f"=== {booking.company.name} ===",
            'ticket_line': f"Ticket: {booking.booking_reference}",
            'passenger_line': f"Passenger: {booking.passenger_name}",
            'route_line': f"Route: {ticket_data['route']}",
            'schedule_line': f"Date: {ticket_data['departure_date']} {ticket_data['departure_time']}",
            'seat_line': f"Seat: {booking.seat.seat_number} | Bus: {booking.trip.bus.registration_number}",
            'amount_line': f"Amount: UGX {booking.total_amount}",
            'footer': "Thank you for choosing us!",
            'terms': "Terms: Present this ticket before boarding"
        }
    
    return ticket_data


def send_sms_ticket(booking, ticket_data):
    """
    Send SMS ticket to passenger
    """
    if not settings.SMS_API_KEY or not settings.SMS_API_URL:
        return False
    
    message = f"""
BOOKUTU TICKET
Ref: {booking.booking_reference}
Passenger: {booking.passenger_name}
Route: {ticket_data['route']}
Date: {ticket_data['departure_date']} {ticket_data['departure_time']}
Seat: {booking.seat.seat_number}
Bus: {booking.trip.bus.registration_number}
Amount: UGX {booking.total_amount}
Driver: {booking.trip.driver_name} ({booking.trip.driver_phone})

Present this SMS at boarding.
Safe travels!
""".strip()
    
    try:
        # This is a generic SMS API call - adjust based on your SMS provider
        response = requests.post(
            settings.SMS_API_URL,
            headers={
                'Authorization': f'Bearer {settings.SMS_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'to': booking.passenger_phone,
                'message': message,
                'from': 'BOOKUTU'
            },
            timeout=10
        )
        
        return response.status_code == 200
    
    except Exception as e:
        # Log the error in production
        print(f"SMS sending failed: {e}")
        return False


def validate_phone_number(phone_number):
    """
    Validate and format phone number for Uganda
    """
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, phone_number))
    
    # Handle different formats
    if phone.startswith('0'):
        phone = '256' + phone[1:]  # Convert 0xxx to 256xxx
    elif phone.startswith('256'):
        pass  # Already in correct format
    elif len(phone) == 9:
        phone = '256' + phone  # Add country code
    else:
        return None
    
    # Validate length and format
    if len(phone) == 12 and phone.startswith('256'):
        return '+' + phone
    
    return None


def calculate_booking_pricing(trip, seat, discount_percentage=0):
    """
    Calculate pricing for a booking
    """
    base_fare = trip.base_fare
    seat_fee = base_fare * (seat.price_multiplier - 1)
    
    # Apply discount if any
    if discount_percentage > 0:
        discount_amount = (base_fare + seat_fee) * (discount_percentage / 100)
        base_fare -= discount_amount * (base_fare / (base_fare + seat_fee))
        seat_fee -= discount_amount * (seat_fee / (base_fare + seat_fee))
    
    service_fee = 0  # No service fee for direct bookings
    total_amount = base_fare + seat_fee + service_fee
    
    return {
        'base_fare': base_fare,
        'seat_fee': seat_fee,
        'service_fee': service_fee,
        'total_amount': total_amount,
        'discount_applied': discount_percentage > 0
    }


def cleanup_expired_reservations():
    """
    Cleanup expired seat reservations
    """
    from .models import SeatReservation
    
    expired_count = SeatReservation.objects.filter(
        is_active=True,
        expires_at__lt=timezone.now()
    ).update(is_active=False)
    
    return expired_count
