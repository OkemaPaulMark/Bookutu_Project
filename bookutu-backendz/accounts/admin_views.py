import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from companies.models import Company, Bus, Driver, CompanySettings
from trips.models import Route, Trip
from bookings.models import Booking
from accounts.models import User
from bookutu.models import SystemSettings, Advert
from .admin_forms import (
    CompanyForm, SystemSettingsForm, SuperUserCreationForm,
    CompanySearchForm, BookingSearchForm, FinancialReportForm
)

logger = logging.getLogger(__name__)


@login_required
def admin_dashboard(request):
    """Super admin dashboard with platform statistics"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    # Calculate statistics
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Platform statistics
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(status='ACTIVE').count()
    verified_companies = Company.objects.filter(verified_at__isnull=False).count()
    
    total_staff = User.objects.filter(user_type='COMPANY_STAFF').count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(
        status='CONFIRMED'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Monthly growth
    new_companies_this_month = Company.objects.filter(
        created_at__date__gte=this_month
    ).count()
    
    new_bookings_this_month = Booking.objects.filter(
        created_at__date__gte=this_month
    ).count()
    
    # Recent activities
    recent_companies = Company.objects.order_by('-created_at')[:5]
    recent_bookings = Booking.objects.select_related(
        'company', 'trip__route'
    ).order_by('-created_at')[:5]
    
    # Bus statistics
    total_buses = Bus.objects.count()
    active_buses = Bus.objects.filter(status='ACTIVE').count()
    maintenance_buses = Bus.objects.filter(status='MAINTENANCE').count()
    
    context = {
        'total_companies': total_companies,
        'active_companies': active_companies,
        'verified_companies': verified_companies,
        'total_staff': total_staff,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'new_companies_this_month': new_companies_this_month,
        'new_bookings_this_month': new_bookings_this_month,
        'recent_companies': recent_companies,
        'recent_bookings': recent_bookings,
        'total_buses': total_buses,
        'active_buses': active_buses,
        'maintenance_buses': maintenance_buses,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def admin_companies(request):
    """List and manage all companies"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    search_form = CompanySearchForm(request.GET)
    companies = Company.objects.all()
    
    # Apply filters
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        status = search_form.cleaned_data.get('status')
        
        if search:
            companies = companies.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        if status:
            companies = companies.filter(status=status)
    
    # Pagination
    paginator = Paginator(companies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'search': request.GET.get('search', ''),
        'status': request.GET.get('status', ''),
    }
    
    return render(request, 'admin/companies.html', context)


@login_required
def company_detail(request, company_id):
    """View detailed company information"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    company = get_object_or_404(Company, id=company_id)
    
    # Get company statistics
    total_buses = Bus.objects.filter(company=company).count()
    active_buses = Bus.objects.filter(company=company, status='ACTIVE').count()
    total_drivers = Driver.objects.filter(company=company).count()
    total_routes = Route.objects.filter(company=company).count()
    total_bookings = Booking.objects.filter(company=company).count()
    total_revenue = Booking.objects.filter(
        company=company, status='CONFIRMED'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Recent bookings
    recent_bookings = Booking.objects.filter(
        company=company
    ).select_related('trip__route').order_by('-created_at')[:10]
    
    context = {
        'company': company,
        'total_buses': total_buses,
        'active_buses': active_buses,
        'total_drivers': total_drivers,
        'total_routes': total_routes,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'admin/company_detail.html', context)


@login_required
def create_company(request):
    """Create a new company"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()

            # Optionally provision initial company staff account using provided credentials
            staff_email = request.POST.get('staff_email') or company.email
            staff_password = request.POST.get('staff_password')
            staff_first_name = request.POST.get('staff_first_name', '').strip() or company.name.split(' ')[0]
            staff_last_name = request.POST.get('staff_last_name', '').strip() or 'Admin'

            if staff_email and staff_password:
                # Create or update the initial staff user
                user, created = User.objects.get_or_create(
                    email=staff_email,
                    defaults={
                        'first_name': staff_first_name,
                        'last_name': staff_last_name,
                        'user_type': 'COMPANY_STAFF',
                        'company': company,
                        'is_active': True,
                    }
                )
                user.first_name = staff_first_name
                user.last_name = staff_last_name
                user.user_type = 'COMPANY_STAFF'
                user.company = company
                user.is_active = True
                user.set_password(staff_password)
                user.save()
                messages.success(request, f'Initial staff account created: {staff_email}')

            messages.success(request, f'Company "{company.name}" created successfully.')
            return redirect('super_admin:company_detail', company_id=company.id)
    else:
        form = CompanyForm()
    
    return render(request, 'admin/create_company.html', {'form': form})


@login_required
def edit_company(request, company_id):
    """Edit company information"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f'Company "{company.name}" updated successfully.')
            return redirect('super_admin:company_detail', company_id=company.id)
    else:
        form = CompanyForm(instance=company)
    
    return render(request, 'admin/edit_company.html', {'form': form, 'company': company})


@login_required
def admin_bookings(request):
    """List and manage all bookings across companies"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    search_form = BookingSearchForm(request.GET)
    bookings = Booking.objects.select_related(
        'company', 'trip__route', 'trip__bus'
    ).order_by('-created_at')
    
    # Apply filters
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        status = search_form.cleaned_data.get('status')
        company = search_form.cleaned_data.get('company')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if search:
            bookings = bookings.filter(
                Q(booking_reference__icontains=search) |
                Q(passenger_name__icontains=search) |
                Q(passenger_phone__icontains=search)
            )
        
        if status:
            bookings = bookings.filter(status=status)
        
        if company:
            bookings = bookings.filter(company=company)
        
        if date_from:
            bookings = bookings.filter(created_at__date__gte=date_from)
        
        if date_to:
            bookings = bookings.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(bookings, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    
    return render(request, 'admin/bookings.html', context)


@login_required
def booking_detail(request, booking_id):
    """View detailed booking information"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    return render(request, 'admin/booking_detail.html', {'booking': booking})


@login_required
def admin_financials(request):
    """Financial reports and analytics"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    report_form = FinancialReportForm(request.GET)
    
    # Default to current month
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Get date range
    date_from = this_month
    date_to = today
    
    if report_form.is_valid():
        period = report_form.cleaned_data.get('period', 'month')
        custom_date_from = report_form.cleaned_data.get('date_from')
        custom_date_to = report_form.cleaned_data.get('date_to')
        
        if period == 'today':
            date_from = today
            date_to = today
        elif period == 'week':
            date_from = today - timedelta(days=7)
        elif period == 'month':
            date_from = this_month
        elif period == 'quarter':
            date_from = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
        elif period == 'year':
            date_from = today.replace(month=1, day=1)
        elif period == 'custom' and custom_date_from and custom_date_to:
            date_from = custom_date_from
            date_to = custom_date_to
    
    # Calculate financial data
    bookings = Booking.objects.filter(
        created_at__date__range=[date_from, date_to],
        status='CONFIRMED'
    )
    
    total_revenue = bookings.aggregate(total=Sum('total_amount'))['total'] or 0
    total_bookings = bookings.count()
    
    # Revenue by company
    revenue_by_company = bookings.values('company__name').annotate(
        revenue=Sum('total_amount'),
        bookings=Count('id')
    ).order_by('-revenue')
    
    # Daily revenue for chart
    daily_revenue = bookings.extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        revenue=Sum('total_amount')
    ).order_by('day')
    
    context = {
        'report_form': report_form,
        'date_from': date_from,
        'date_to': date_to,
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'revenue_by_company': revenue_by_company,
        'daily_revenue': daily_revenue,
    }
    
    return render(request, 'admin/financials.html', context)


@login_required
def admin_logs(request):
    """System logs and audit trail"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    # For now, we'll show recent activities
    # In a real system, you'd have a proper logging system
    recent_companies = Company.objects.order_by('-created_at')[:20]
    recent_bookings = Booking.objects.select_related(
        'company', 'trip__route'
    ).order_by('-created_at')[:20]
    
    context = {
        'recent_companies': recent_companies,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'admin/logs.html', context)


@login_required
def admin_settings(request):
    """System settings management"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    # Get or create system settings
    settings, created = SystemSettings.objects.get_or_create(
        defaults={
            'platform_name': 'Bookutu',
            'platform_email': 'admin@bookutu.com',
            'platform_phone': '+256 700 000000',
            'currency': 'UGX',
            'timezone': 'Africa/Kampala',
        }
    )
    
    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'System settings updated successfully.')
            return redirect('super_admin:admin_settings')
    else:
        form = SystemSettingsForm(instance=settings)
    
    return render(request, 'admin/settings.html', {'form': form, 'settings': settings})


@login_required
def admin_adverts(request):
    """List and manage all adverts"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    adverts = Advert.objects.all().order_by('-created_at')
    return render(request, 'admin/adverts.html', { 'adverts': adverts })


@login_required
def create_advert(request):
    """Create a new advert"""
    logger.info(f"User {request.user} attempting to create advert")
    if not request.user.is_superuser:
        logger.warning(f"Non-superuser {request.user} tried to create advert")
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    from .admin_forms import AdvertForm
    if request.method == 'POST':
        logger.info("POST request for advert creation")
        form = AdvertForm(request.POST, request.FILES)
        logger.info(f"Form data: {request.POST}")
        logger.info(f"Files: {request.FILES}")
        if form.is_valid():
            logger.info("Form is valid, attempting to save")
            try:
                advert = form.save()
                logger.info(f"Advert saved successfully: {advert.title} (id: {advert.id})")
                messages.success(request, f'Advert "{advert.title}" created successfully.')
                return redirect('super_admin:admin_adverts')
            except Exception as e:
                logger.error(f"Error saving advert: {e}")
                messages.error(request, 'Error saving advert. Please try again.')
        else:
            logger.warning(f"Form is invalid. Errors: {form.errors}")
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        logger.info("GET request for advert creation form")
        form = AdvertForm()
    return render(request, 'admin/create_advert.html', { 'form': form })


@login_required
def edit_advert(request, advert_id):
    """Edit an existing advert"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    from .admin_forms import AdvertForm
    advert = get_object_or_404(Advert, id=advert_id)
    if request.method == 'POST':
        form = AdvertForm(request.POST, request.FILES, instance=advert)
        if form.is_valid():
            form.save()
            messages.success(request, f'Advert "{advert.title}" updated successfully.')
            return redirect('super_admin:admin_adverts')
    else:
        form = AdvertForm(instance=advert)
    return render(request, 'admin/edit_advert.html', { 'form': form, 'advert': advert })


@login_required
def toggle_advert_status(request, advert_id):
    """Activate or deactivate an advert"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    advert = get_object_or_404(Advert, id=advert_id)
    advert.is_active = not advert.is_active
    advert.save()
    status = 'activated' if advert.is_active else 'deactivated'
    messages.success(request, f'Advert "{advert.title}" {status} successfully.')
    return redirect('super_admin:admin_adverts')


@login_required
def delete_advert(request, advert_id):
    """Delete an advert"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    advert = get_object_or_404(Advert, id=advert_id)
    advert.delete()
    messages.success(request, f'Advert "{advert.title}" deleted successfully.')
    return redirect('super_admin:admin_adverts')


@login_required
def create_superuser(request):
    """Create a new super admin user"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    if request.method == 'POST':
        form = SuperUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Super admin "{user.get_full_name()}" created successfully.')
            return redirect('super_admin:admin_dashboard')
    else:
        form = SuperUserCreationForm()
    
    return render(request, 'admin/create_superuser.html', {'form': form})


@login_required
def toggle_company_status(request, company_id):
    """Toggle company active status"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    company = get_object_or_404(Company, id=company_id)
    if company.status == 'ACTIVE':
        company.status = 'INACTIVE'
        status = 'deactivated'
    else:
        company.status = 'ACTIVE'
        status = 'activated'
    company.save()
    
    messages.success(request, f'Company "{company.name}" {status} successfully.')
    
    return redirect('super_admin:company_detail', company_id=company.id)


@login_required
def toggle_company_verification(request, company_id):
    """Toggle company verification status"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Super admin privileges required.')
        return redirect('company:dashboard')
    
    company = get_object_or_404(Company, id=company_id)
    if company.verified_at:
        company.verified_at = None
        status = 'unverified'
    else:
        company.verified_at = timezone.now()
        status = 'verified'
    company.save()
    
    messages.success(request, f'Company "{company.name}" {status} successfully.')
    
    return redirect('super_admin:company_detail', company_id=company.id)