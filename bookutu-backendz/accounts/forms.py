from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User, PassengerProfile
from companies.models import Company
from django.core.exceptions import ValidationError
from django.db import transaction


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter your email address',
            'required': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter your password',
            'required': True,
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email Address'
        self.fields['password'].label = 'Password'





class CompanyStaffRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter staff email address',
            'required': True,
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter first name',
            'required': True,
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter last name',
            'required': True,
        })
    )
    role = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter staff role (e.g., Manager, Operator)',
            'required': True,
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Create a password',
            'required': True,
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Confirm password',
            'required': True,
        })
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def __init__(self, company=None, *args, **kwargs):
        self.company = company
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = User.COMPANY_STAFF
        user.company = self.company
        if commit:
            user.save()
        return user


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors',
            'placeholder': 'Enter your email address',
            'required': True,
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email address.")
        return email


class CompanyRegistrationForm(forms.Form):
    """Combined form to register a new company and its initial staff admin user."""

    # Company fields
    company_name = forms.CharField(max_length=200)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea, max_length=1000)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100, initial='Uganda')
    registration_number = forms.CharField(max_length=100)
    license_number = forms.CharField(max_length=100)

    # Initial staff user fields
    staff_first_name = forms.CharField(max_length=30)
    staff_last_name = forms.CharField(max_length=30)
    staff_email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        if data.get('password1') != data.get('password2'):
            raise ValidationError('Passwords do not match.')
        if User.objects.filter(email=data.get('staff_email')).exists():
            raise ValidationError('An account with this staff email already exists.')
        if Company.objects.filter(registration_number=data.get('registration_number')).exists():
            raise ValidationError('A company with this registration number already exists.')
        return data

    @transaction.atomic
    def save(self) -> User:
        company = Company.objects.create(
            name=self.cleaned_data['company_name'],
            email=self.cleaned_data['email'],
            phone_number=self.cleaned_data['phone_number'],
            address=self.cleaned_data['address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            country=self.cleaned_data['country'],
            registration_number=self.cleaned_data['registration_number'],
            license_number=self.cleaned_data['license_number'],
            status='ACTIVE',
        )

        user = User.objects.create(
            email=self.cleaned_data['staff_email'],
            first_name=self.cleaned_data['staff_first_name'],
            last_name=self.cleaned_data['staff_last_name'],
            user_type='COMPANY_STAFF',
            company=company,
            is_active=True,
        )
        user.set_password(self.cleaned_data['password1'])
        user.save()
        return user
