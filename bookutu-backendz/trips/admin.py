from django.contrib import admin
from .models import Route, Trip, TripPricing


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "origin_city",
        "destination_city",
        "distance_km",
        "estimated_duration_hours",
        "base_fare",
    )
    list_filter = ("company", "is_active")
    search_fields = ("name", "origin_city", "destination_city")
    ordering = ("origin_city", "destination_city")


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "company",
        "departure_date",
        "departure_time",
        "bus",
        "driver",
        "status",
        "available_seats",
        "booked_seats",
    )
    list_filter = ("status", "company", "departure_date", "driver")
    search_fields = (
        "route__name",
        "bus__license_plate",
        "driver__first_name",
        "driver__last_name",
    )
    ordering = ("-departure_date", "departure_time")
    raw_id_fields = (
        "driver",
    )  # Use raw_id_fields for ForeignKey to User for better performance with many users


@admin.register(TripPricing)
class TripPricingAdmin(admin.ModelAdmin):
    list_display = (
        "trip",
        "peak_season_multiplier",
        "demand_multiplier",
        "early_bird_discount",
        "final_base_fare",
    )
    search_fields = ("trip__route__name",)
    ordering = ("trip",)
