from django import forms
from django.contrib.auth import get_user_model
from .models import Booking, BookingCancellation
from companies.models import BusSeat
from trips.models import Trip

User = get_user_model()


class DirectBookingForm(forms.ModelForm):
    """Form for creating direct bookings (by company staff for customers)"""
    
    class Meta:
        model = Booking
        fields = [
            'trip', 'seat', 'passenger_name', 'passenger_phone', 'passenger_email',
            'base_fare', 'seat_fee', 'service_fee', 'total_amount', 'source'
        ]
        widgets = {
            'trip': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'seat': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'passenger_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Passenger Full Name'
            }),
            'passenger_phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '+256 700 123456'
            }),
            'passenger_email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'passenger@example.com'
            }),
            'base_fare': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01',
                'placeholder': '35000'
            }),
            'seat_fee': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01',
                'placeholder': '0'
            }),
            'service_fee': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01',
                'placeholder': '0'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01',
                'placeholder': '35000'
            }),
            'source': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            # Filter trips to only show those belonging to the company
            self.fields['trip'].queryset = Trip.objects.filter(company=company)
            # Filter seats to only show those belonging to company buses
            self.fields['seat'].queryset = BusSeat.objects.filter(bus__company=company)
    
    def clean(self):
        cleaned_data = super().clean()
        trip = cleaned_data.get('trip')
        seat = cleaned_data.get('seat')
        
        if trip and seat:
            # Check if seat belongs to the trip's bus
            if seat.bus != trip.bus:
                raise forms.ValidationError("Selected seat does not belong to the trip's bus.")
            
            # Check if seat is already booked for this trip
            existing_booking = Booking.objects.filter(
                trip=trip,
                seat=seat,
                status__in=['PENDING', 'CONFIRMED']
            ).exists()
            
            if existing_booking:
                raise forms.ValidationError("This seat is already booked for this trip.")
        
        return cleaned_data


class BookingUpdateForm(forms.ModelForm):
    """Form for updating booking details"""
    
    class Meta:
        model = Booking
        fields = [
            'status', 'passenger_name', 'passenger_phone', 'passenger_email',
            'base_fare', 'seat_fee', 'service_fee', 'total_amount'
        ]
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'passenger_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Passenger Full Name'
            }),
            'passenger_phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '+256 700 123456'
            }),
            'passenger_email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'passenger@example.com'
            }),
            'base_fare': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01'
            }),
            'seat_fee': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01'
            }),
            'service_fee': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01'
            }),
        }


class BookingCancellationForm(forms.ModelForm):
    """Form for cancelling bookings"""
    
    class Meta:
        model = BookingCancellation
        fields = ['reason', 'cancellation_fee', 'refund_amount']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Reason for cancellation...'
            }),
            'cancellation_fee': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01',
                'placeholder': '0'
            }),
            'refund_amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'step': '0.01',
                'placeholder': '0'
            }),
        }


class BookingSearchForm(forms.Form):
    """Form for searching bookings"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Search by booking reference, passenger name, or phone...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Booking.BOOKING_STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'type': 'date'
        })
    )