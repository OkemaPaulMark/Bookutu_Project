from django import forms
from .models import Route, Trip, TripPricing
from companies.models import Bus
from django.contrib.auth import get_user_model

User = get_user_model()


class RouteForm(forms.ModelForm):
    """Form for creating and editing routes"""

    class Meta:
        model = Route
        fields = [
            "name",
            "origin_city",
            "origin_terminal",
            "destination_city",
            "destination_terminal",
            "distance_km",
            "estimated_duration_hours",
            "base_fare",
            "is_active",
            "intermediate_stops",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Kampala to Gulu Express",
                }
            ),
            "origin_city": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Kampala",
                }
            ),
            "origin_terminal": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Kampala Bus Terminal",
                }
            ),
            "destination_city": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Gulu",
                }
            ),
            "destination_terminal": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Gulu Bus Terminal",
                }
            ),
            "distance_km": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": "1",
                    "placeholder": "332",
                }
            ),
            "estimated_duration_hours": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": "0.1",
                    "step": "0.1",
                    "placeholder": "5.5",
                }
            ),
            "base_fare": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "35000",
                }
            ),
            "intermediate_stops": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 3,
                    "placeholder": 'Enter stops as JSON: [{"city": "Lira", "duration_minutes": 30}]',
                }
            ),
        }


class TripForm(forms.ModelForm):
    """Form for creating and editing trips"""

    class Meta:
        model = Trip
        fields = [
            "route",
            "bus",
            "departure_date",
            "departure_time",
            "arrival_time",
            "base_fare",
            "status",
            "driver_name",
            "driver_phone",
            "conductor_name",
            "conductor_phone",
            "notes",
        ]
        widgets = {
            "route": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            ),
            "bus": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            ),
            "departure_date": forms.DateInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "type": "date",
                }
            ),
            "departure_time": forms.TimeInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "type": "time",
                }
            ),
            "arrival_time": forms.TimeInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "type": "time",
                }
            ),
            "base_fare": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "35000",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            ),
            "driver_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Driver Name",
                }
            ),
            "driver_phone": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "+256 772 123456",
                }
            ),
            "conductor_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Conductor Name (Optional)",
                }
            ),
            "conductor_phone": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "+256 700 987654",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 3,
                    "placeholder": "Additional notes...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

        if self.company:
            # Filter routes and buses to only show those belonging to the company
            self.fields["route"].queryset = Route.objects.filter(company=self.company)
            self.fields["bus"].queryset = Bus.objects.filter(company=self.company)

            # Set company on instance if it's a new instance
            if not self.instance.pk and self.company:
                self.instance.company = self.company

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        if commit:
            instance.save()
        return instance


class AssignDriverForm(forms.ModelForm):
    """Assign a driver (company staff) to a trip"""

    class Meta:
        model = Trip
        fields = ["driver"]
        widgets = {
            "driver": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields["driver"].queryset = User.objects.filter(
                company=company,
                user_type="COMPANY_STAFF",
                is_active=True,
            ).order_by("first_name", "last_name")


class TripPricingForm(forms.ModelForm):
    """Form for editing trip pricing"""

    class Meta:
        model = TripPricing
        fields = [
            "peak_season_multiplier",
            "demand_multiplier",
            "early_bird_discount",
            "early_bird_days",
        ]
        widgets = {
            "peak_season_multiplier": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": "0.1",
                    "step": "0.01",
                    "placeholder": "1.00",
                }
            ),
            "demand_multiplier": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": "0.1",
                    "step": "0.01",
                    "placeholder": "1.00",
                }
            ),
            "early_bird_discount": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": "0",
                    "max": "1",
                    "step": "0.01",
                    "placeholder": "0.10",
                }
            ),
            "early_bird_days": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": "1",
                    "max": "30",
                    "placeholder": "7",
                }
            ),
        }
