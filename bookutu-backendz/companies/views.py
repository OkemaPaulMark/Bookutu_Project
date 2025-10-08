from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Company, Bus, Driver, CompanySettings
from .forms import CompanyForm, BusForm, DriverForm, CompanySettingsForm, CompanyStaffForm
from trips.models import Route, Trip
from bookings.models import Booking
from accounts.models import User


@login_required
def company_dashboard(request):
    """Company dashboard with statistics and recent activity"""
    company = request.user.company
    
    # Calculate statistics
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Today's bookings
    today_bookings = Booking.objects.filter(
        company=company,
        created_at__date=today
    ).count()
    
    # Active buses
    active_buses = Bus.objects.filter(company=company, status='ACTIVE').count()
    
    # Active routes
    active_routes = Route.objects.filter(company=company, is_active=True).count()
    
    # Monthly revenue
    monthly_revenue = Booking.objects.filter(
        company=company,
        created_at__date__gte=this_month,
        status='CONFIRMED'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Recent bookings
    recent_bookings = Booking.objects.filter(
        company=company
    ).select_related('trip', 'seat').order_by('-created_at')[:5]
    
    # Fleet status
    fleet_status = Bus.objects.filter(company=company).values('status').annotate(
        count=Count('id')
    )
    
    context = {
        'today_bookings': today_bookings,
        'active_buses': active_buses,
        'active_routes': active_routes,
        'monthly_revenue': monthly_revenue,
        'recent_bookings': recent_bookings,
        'fleet_status': fleet_status,
    }
    
    return render(request, 'company/dashboard.html', context)


@login_required
def company_bookings(request):
    """List and manage bookings"""
    company = request.user.company
    
    # Get search parameters
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Build query
    bookings = Booking.objects.filter(company=company).select_related(
        'trip', 'seat', 'passenger'
    ).order_by('-created_at')
    
    if search:
        bookings = bookings.filter(
            Q(booking_reference__icontains=search) |
            Q(passenger_name__icontains=search) |
            Q(passenger_phone__icontains=search)
        )
    
    if status:
        bookings = bookings.filter(status=status)
    
    if date_from:
        bookings = bookings.filter(created_at__date__gte=date_from)
    
    if date_to:
        bookings = bookings.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(bookings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'company/bookings.html', context)


@login_required
def booking_detail(request, booking_id):
    """View booking details"""
    company = request.user.company
    booking = get_object_or_404(Booking, id=booking_id, company=company)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'company/booking_detail.html', context)


@login_required
def create_booking(request):
    """Create a new booking"""
    company = request.user.company
    
    if request.method == 'POST':
        from bookings.forms import DirectBookingForm
        form = DirectBookingForm(request.POST, company=company)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.company = company
            booking.booked_by = request.user
            booking.passenger = request.user  # For now, use the staff member as passenger
            booking.save()
            messages.success(request, 'Booking created successfully!')
            return redirect('company:booking_detail', booking_id=booking.id)
    else:
        from bookings.forms import DirectBookingForm
        form = DirectBookingForm(company=company)
    
    context = {
        'form': form,
    }
    
    return render(request, 'company/create_booking.html', context)


@login_required
def company_fleet(request):
    """List and manage fleet"""
    company = request.user.company
    
    # Get search parameter
    search = request.GET.get('search', '')
    
    buses = Bus.objects.filter(company=company).order_by('license_plate')
    
    if search:
        buses = buses.filter(
            Q(license_plate__icontains=search) |
            Q(model__icontains=search) |
            Q(make__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(buses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'company/fleet.html', context)


@login_required
def bus_detail(request, bus_id):
    """View bus details"""
    company = request.user.company
    bus = get_object_or_404(Bus, id=bus_id, company=company)
    
    # Get upcoming trips for this bus
    upcoming_trips = Trip.objects.filter(
        bus=bus,
        departure_date__gte=timezone.now().date()
    ).order_by('departure_date', 'departure_time')[:5]
    
    context = {
        'bus': bus,
        'upcoming_trips': upcoming_trips,
    }
    
    return render(request, 'company/bus_detail.html', context)


@login_required
def create_bus(request):
    """Create a new bus"""
    company = request.user.company
    
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES)
        if form.is_valid():
            bus = form.save(commit=False)
            bus.company = company
            bus.save()
            messages.success(request, 'Bus added successfully!')
            return redirect('company:bus_detail', bus_id=bus.id)
    else:
        form = BusForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'company/create_bus.html', context)


@login_required
def edit_bus(request, bus_id):
    """Edit bus details"""
    company = request.user.company
    bus = get_object_or_404(Bus, id=bus_id, company=company)
    
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus updated successfully!')
            return redirect('company:bus_detail', bus_id=bus.id)
    else:
        form = BusForm(instance=bus)
    
    context = {
        'form': form,
        'bus': bus,
    }
    
    return render(request, 'company/edit_bus.html', context)


@login_required
def company_routes(request):
    """List and manage routes"""
    company = request.user.company
    
    # Get search parameter
    search = request.GET.get('search', '')
    
    routes = Route.objects.filter(company=company).order_by('origin_city', 'destination_city')
    
    if search:
        routes = routes.filter(
            Q(name__icontains=search) |
            Q(origin_city__icontains=search) |
            Q(destination_city__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(routes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'company/routes.html', context)


@login_required
def route_detail(request, route_id):
    """View route details"""
    company = request.user.company
    route = get_object_or_404(Route, id=route_id, company=company)
    
    # Get upcoming trips for this route
    upcoming_trips = Trip.objects.filter(
        route=route,
        departure_date__gte=timezone.now().date()
    ).order_by('departure_date', 'departure_time')[:10]
    
    context = {
        'route': route,
        'upcoming_trips': upcoming_trips,
    }
    
    return render(request, 'company/route_detail.html', context)


@login_required
def create_route(request):
    """Create a new route"""
    company = request.user.company
    
    if request.method == 'POST':
        from trips.forms import RouteForm
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.company = company
            route.save()
            messages.success(request, 'Route created successfully!')
            return redirect('company:route_detail', route_id=route.id)
    else:
        from trips.forms import RouteForm
        form = RouteForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'company/create_route.html', context)


@login_required
def edit_route(request, route_id):
    """Edit route details"""
    company = request.user.company
    route = get_object_or_404(Route, id=route_id, company=company)
    
    if request.method == 'POST':
        from trips.forms import RouteForm
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route updated successfully!')
            return redirect('company:route_detail', route_id=route.id)
    else:
        from trips.forms import RouteForm
        form = RouteForm(instance=route)
    
    context = {
        'form': form,
        'route': route,
    }
    
    return render(request, 'company/edit_route.html', context)


@login_required
def company_drivers(request):
    """List and manage drivers"""
    company = request.user.company
    
    # Get search parameter
    search = request.GET.get('search', '')
    
    drivers = Driver.objects.filter(company=company).order_by('last_name', 'first_name')
    
    if search:
        drivers = drivers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(license_number__icontains=search) |
            Q(phone_number__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(drivers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'company/drivers.html', context)


@login_required
def driver_detail(request, driver_id):
    """View driver details"""
    company = request.user.company
    driver = get_object_or_404(Driver, id=driver_id, company=company)

    # Get recent trips for this driver
    recent_trips = Trip.objects.filter(
        driver_name__icontains=driver.first_name,
        company=company
    ).order_by('-departure_date')[:10]

    # Calculate license status
    today = timezone.now().date()
    days_until_expiry = (driver.license_expiry_date - today).days

    if days_until_expiry < 0:
        license_status = 'expired'
    elif days_until_expiry <= 30:
        license_status = 'expiring_soon'
    else:
        license_status = 'valid'

    context = {
        'driver': driver,
        'recent_trips': recent_trips,
        'license_status': license_status,
        'days_until_expiry': max(0, days_until_expiry),
    }

    return render(request, 'company/driver_detail.html', context)


@login_required
def create_driver(request):
    """Create a new driver"""
    company = request.user.company
    
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.company = company
            driver.save()
            messages.success(request, 'Driver added successfully!')
            return redirect('company:driver_detail', driver_id=driver.id)
    else:
        form = DriverForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'company/create_driver.html', context)


@login_required
def edit_driver(request, driver_id):
    """Edit driver details"""
    company = request.user.company
    driver = get_object_or_404(Driver, id=driver_id, company=company)
    
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver updated successfully!')
            return redirect('company:driver_detail', driver_id=driver.id)
    else:
        form = DriverForm(instance=driver)
    
    context = {
        'form': form,
        'driver': driver,
    }
    
    return render(request, 'company/edit_driver.html', context)


@login_required
def company_reports(request):
    """Company reports and analytics"""
    company = request.user.company
    
    # Date range for reports
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Booking statistics
    bookings = Booking.objects.filter(
        company=company,
        created_at__date__range=[start_date, end_date]
    )
    
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status='CONFIRMED').count()
    total_revenue = bookings.filter(status='CONFIRMED').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Route performance
    route_performance = bookings.values('trip__route__name').annotate(
        booking_count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('-booking_count')[:10]
    
    # Daily booking trends
    daily_bookings = bookings.extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    context = {
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
        'route_performance': route_performance,
        'daily_bookings': daily_bookings,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'company/reports.html', context)


@login_required
def company_settings(request):
    """Company settings management"""
    company = request.user.company
    
    # Get or create company settings
    settings, created = CompanySettings.objects.get_or_create(company=company)
    
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('company:settings')
    else:
        form = CompanySettingsForm(instance=settings)
    
    context = {
        'form': form,
        'company': company,
    }
    
    return render(request, 'company/settings.html', context)


@login_required
def create_staff(request):
    """Create new company staff member"""
    company = request.user.company
    
    if request.method == 'POST':
        form = CompanyStaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.company = company
            staff.save()
            messages.success(request, 'Staff member added successfully!')
            return redirect('company:staff_list')
    else:
        form = CompanyStaffForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'company/create_staff.html', context)


@login_required
def staff_list(request):
    """List company staff members"""
    company = request.user.company
    
    staff_members = User.objects.filter(
        company=company,
        user_type='COMPANY_STAFF'
    ).order_by('first_name', 'last_name')
    
    context = {
        'staff_members': staff_members,
    }
    
    return render(request, 'company/staff_list.html', context)