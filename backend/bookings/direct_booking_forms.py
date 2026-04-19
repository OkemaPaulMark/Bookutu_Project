from django import forms
from .models import Booking
from trips.models import Trip


class DirectBookingTripForm(forms.Form):
    trip = forms.ModelChoiceField(
        queryset=Trip.objects.none(),
        widget=forms.HiddenInput()
    )
    
    def __init__(self, company, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trip'].queryset = Trip.objects.filter(
            bus__company=company,
            departure_time__gte=timezone.now()
        ).select_related('route', 'bus')


class DirectBookingPassengerForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter first name',
            'required': True,
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter last name',
            'required': True,
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter phone number',
            'required': True,
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter email address (optional)',
        })
    )
    id_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'ID or passport number (optional)',
        })
    )


class DirectBookingSeatForm(forms.Form):
    selected_seats = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def __init__(self, trip, *args, **kwargs):
        self.trip = trip
        super().__init__(*args, **kwargs)
    
    def clean_selected_seats(self):
        selected_seats = self.cleaned_data['selected_seats']
        if not selected_seats:
            raise forms.ValidationError("Please select at least one seat.")
        
        seat_numbers = [int(s.strip()) for s in selected_seats.split(',')]
        
        # Check if seats are available
        booked_seats = list(self.trip.bookings.filter(
            status__in=['CONFIRMED', 'CHECKED_IN']
        ).values_list('seat_numbers', flat=True))
        
        for seat_num in seat_numbers:
            if seat_num in booked_seats:
                raise forms.ValidationError(f"Seat {seat_num} is already booked.")
        
        return selected_seats


class DirectBookingPaymentForm(forms.Form):
    PAYMENT_METHODS = [
        ('CASH', 'Cash Payment'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('ALREADY_PAID', 'Already Paid'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect()
    )
    
    # Mobile money fields
    mobile_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring',
            'placeholder': 'Enter mobile number',
        })
    )
    mobile_provider = forms.ChoiceField(
        choices=[
            ('', 'Select provider'),
            ('MTN', 'MTN Mobile Money'),
            ('AIRTEL', 'Airtel Money'),
            ('VODAFONE', 'Vodafone Cash'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring',
        })
    )
    
    # Notes field
    payment_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring',
            'placeholder': 'Additional payment notes (optional)',
            'rows': 2,
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'MOBILE_MONEY':
            if not cleaned_data.get('mobile_number'):
                raise forms.ValidationError("Mobile number is required for mobile money payments.")
            if not cleaned_data.get('mobile_provider'):
                raise forms.ValidationError("Mobile provider is required for mobile money payments.")
        
        return cleaned_data
