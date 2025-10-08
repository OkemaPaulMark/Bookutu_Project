from celery import shared_task
from django.utils import timezone
from .utils import cleanup_expired_reservations, send_sms_ticket, generate_ticket
from .models import Booking
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_seat_reservations():
    """
    Periodic task to cleanup expired seat reservations
    """
    try:
        expired_count = cleanup_expired_reservations()
        logger.info(f"Cleaned up {expired_count} expired seat reservations")
        return f"Cleaned up {expired_count} expired reservations"
    except Exception as e:
        logger.error(f"Error cleaning up reservations: {e}")
        return f"Error: {e}"


@shared_task
def send_booking_reminder_sms(booking_id):
    """
    Send booking reminder SMS before departure
    """
    try:
        booking = Booking.objects.get(id=booking_id, status='CONFIRMED')
        
        # Check if trip is within 24 hours
        trip_datetime = timezone.datetime.combine(
            booking.trip.departure_date,
            booking.trip.departure_time
        )
        trip_datetime = timezone.make_aware(trip_datetime)
        
        hours_until_departure = (trip_datetime - timezone.now()).total_seconds() / 3600
        
        if 0 < hours_until_departure <= 24:
            ticket_data = generate_ticket(booking)
            
            # Customize message for reminder
            reminder_message = f"""
BOOKUTU REMINDER
Your trip is in {int(hours_until_departure)} hours!

Ref: {booking.booking_reference}
Route: {ticket_data['route']}
Date: {ticket_data['departure_date']} {ticket_data['departure_time']}
Seat: {booking.seat.seat_number}
Terminal: {booking.trip.route.origin_terminal}

Please arrive 30 minutes early.
Safe travels!
""".strip()
            
            # Send custom reminder SMS
            success = send_sms_ticket(booking, ticket_data, custom_message=reminder_message)
            
            if success:
                logger.info(f"Reminder SMS sent for booking {booking.booking_reference}")
                return f"Reminder sent for booking {booking.booking_reference}"
            else:
                logger.warning(f"Failed to send reminder for booking {booking.booking_reference}")
                return f"Failed to send reminder for booking {booking.booking_reference}"
        
        return f"Booking {booking.booking_reference} not within reminder window"
        
    except Booking.DoesNotExist:
        logger.error(f"Booking {booking_id} not found for reminder")
        return f"Booking {booking_id} not found"
    except Exception as e:
        logger.error(f"Error sending reminder for booking {booking_id}: {e}")
        return f"Error: {e}"


@shared_task
def generate_daily_booking_report(company_id, date_str):
    """
    Generate daily booking report for a company
    """
    try:
        from companies.models import Company
        from django.core.mail import send_mail
        from django.conf import settings
        
        company = Company.objects.get(id=company_id)
        report_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get bookings for the date
        bookings = Booking.objects.filter(
            company=company,
            created_at__date=report_date
        )
        
        # Generate report data
        report_data = {
            'total_bookings': bookings.count(),
            'confirmed_bookings': bookings.filter(status='CONFIRMED').count(),
            'cancelled_bookings': bookings.filter(status='CANCELLED').count(),
            'total_revenue': float(bookings.filter(status='CONFIRMED').aggregate(
                total=models.Sum('total_amount')
            )['total'] or 0),
            'direct_bookings': bookings.filter(source='DIRECT').count(),
            'online_bookings': bookings.filter(source='MOBILE_APP').count()
        }
        
        # Send email report
        subject = f"Daily Booking Report - {company.name} - {report_date}"
        message = f"""
Daily Booking Report for {company.name}
Date: {report_date}

Summary:
- Total Bookings: {report_data['total_bookings']}
- Confirmed: {report_data['confirmed_bookings']}
- Cancelled: {report_data['cancelled_bookings']}
- Total Revenue: UGX {report_data['total_revenue']:,.2f}
- Direct Bookings: {report_data['direct_bookings']}
- Online Bookings: {report_data['online_bookings']}

This is an automated report from Bookutu.
"""
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [company.email],
            fail_silently=False
        )
        
        logger.info(f"Daily report sent to {company.name}")
        return f"Report sent to {company.name}"
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return f"Error: {e}"
