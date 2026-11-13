"""Periodic trip lifecycle tasks (run by the Celery worker's beat scheduler)."""
import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.core.management import call_command
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def advance_trip_statuses():
    """Move trips through SCHEDULED -> IN_TRANSIT -> COMPLETED as time passes,
    and mark confirmed bookings on finished trips as COMPLETED."""
    from bookings.models import Booking
    from trips.models import Trip

    now = timezone.localtime()
    today = now.date()
    started = completed = 0

    # Look at trips from the last couple of days through today
    for trip in Trip.objects.filter(
        departure_date__gte=today - timedelta(days=2), departure_date__lte=today,
        status__in=["SCHEDULED", "BOARDING", "IN_TRANSIT", "DELAYED"],
    ):
        dep = timezone.make_aware(datetime.combine(trip.departure_date, trip.departure_time))
        arr = timezone.make_aware(datetime.combine(trip.departure_date, trip.arrival_time))
        if now >= arr:
            Trip.objects.filter(pk=trip.pk).update(status="COMPLETED", actual_arrival_time=arr)
            Booking.objects.filter(trip=trip, status="CONFIRMED").update(status="COMPLETED")
            completed += 1
        elif now >= dep and trip.status != "IN_TRANSIT":
            Trip.objects.filter(pk=trip.pk).update(status="IN_TRANSIT", actual_departure_time=dep)
            started += 1

    # Older trips that were never closed out
    old = Trip.objects.filter(departure_date__lt=today - timedelta(days=2),
                              status__in=["SCHEDULED", "BOARDING", "IN_TRANSIT", "DELAYED"])
    Booking.objects.filter(trip__in=old, status="CONFIRMED").update(status="COMPLETED")
    completed += old.update(status="COMPLETED")

    logger.info("Trip statuses: %s departed, %s completed", started, completed)
    return {"departed": started, "completed": completed}


@shared_task
def refresh_demo_trips():
    """Re-seed demo trips when fewer than 3 days of them remain."""
    from trips.models import Trip

    cutoff = timezone.localdate() + timedelta(days=3)
    if Trip.objects.filter(notes="DEMO_SEED", departure_date__gte=cutoff).exists():
        return "demo trips still current"
    call_command("seed_demo")
    return "demo trips reseeded"
