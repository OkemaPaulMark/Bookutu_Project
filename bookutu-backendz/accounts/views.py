from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    CustomTokenObtainPairSerializer, UserRegistrationSerializer,
    CompanyStaffRegistrationSerializer, UserProfileSerializer,
    PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, UserSessionSerializer
)
from .permissions import IsOwnerOrReadOnly, IsSuperAdmin
from .models import PasswordResetToken, UserSession
from .forms import LoginForm, CompanyRegistrationForm
import uuid
from datetime import timedelta

User = get_user_model()


def web_login(request):
    """
    Web-based login view for session authentication
    """

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')

            # Redirect based on user type
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            if user.user_type == 'SUPER_ADMIN':
                return redirect('/admin/')
            elif user.user_type == 'COMPANY_STAFF':
                return redirect('/company/')
            else:
                return redirect('/accounts/login/')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})





def web_password_reset(request):
    """
    Web-based password reset view
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                # Create password reset token
                token = str(uuid.uuid4())
                expires_at = timezone.now() + timedelta(hours=24)
                
                PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=expires_at
                )
                
                messages.success(request, 'Password reset email sent. Please check your inbox.')
                return redirect('/accounts/login/')
            except User.DoesNotExist:
                messages.error(request, 'No account found with that email address.')
        else:
            messages.error(request, 'Please enter your email address.')
    
    return render(request, 'auth/password_reset.html')


def company_register(request):
    """Public company registration: creates Company and initial staff user."""
    from bookutu.models import SystemSettings
    settings = SystemSettings.get_settings()
    if not settings.allow_company_registration:
        messages.error(request, 'Company registration is currently disabled.')
        return redirect('/accounts/login/')

    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Company registered successfully. You can now log in.')
            return redirect('/accounts/login/')
    else:
        form = CompanyRegistrationForm()

    return render(request, 'auth/company_register.html', { 'form': form })


@login_required
def web_logout(request):
    """
    Enhanced web-based logout view with cleanup and analytics
    """
    user = request.user

    # Log logout event for analytics
    from .models import UserSession
    try:
        session = UserSession.objects.filter(
            user=user,
            session_key=request.session.session_key
        ).first()
        if session:
            session.is_active = False
            session.save()
    except:
        pass  # Ignore if session tracking fails

    # Clear any user-specific cache/session data
    if hasattr(request, 'session'):
        # Clear any user-specific session data
        keys_to_clear = [key for key in request.session.keys() if key.startswith('user_')]
        for key in keys_to_clear:
            del request.session[key]

    # Perform Django logout
    logout(request)

    # Add user-type specific logout messages
    if user.user_type == 'SUPER_ADMIN':
        messages.success(request, f'Logged out successfully, {user.get_full_name()}. Super admin session ended.')
    elif user.user_type == 'COMPANY_STAFF':
        messages.success(request, f'Logged out successfully, {user.get_full_name()}. Company session ended.')
    else:
        messages.success(request, f'Logged out successfully, {user.get_full_name()}. See you next time!')

    return redirect('/')


@method_decorator(login_required, name='dispatch')
class DashboardRedirectView(TemplateView):
    """
    Redirect users to their appropriate dashboard
    """
    def get(self, request, *args, **kwargs):
        if request.user.user_type == 'SUPER_ADMIN':
            return redirect('/admin/')
        elif request.user.user_type == 'COMPANY_STAFF':
            return redirect('/company/')
        else:
            return redirect('/accounts/login/')


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view
    """
    serializer_class = CustomTokenObtainPairSerializer





class CompanyStaffRegistrationView(generics.CreateAPIView):
    """
    Company staff registration endpoint (super admin only)
    """
    queryset = User.objects.all()
    serializer_class = CompanyStaffRegistrationSerializer
    permission_classes = [IsSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': 'Company staff created successfully.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile view
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    """
    Password change endpoint
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({'message': 'Password changed successfully.'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Password reset request endpoint
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            # Create password reset token
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(hours=24)

            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )

            # Send password reset email
            self.send_password_reset_email(user, token)

            return Response({'message': 'Password reset email sent.'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_password_reset_email(self, user, token):
        """Send password reset email"""
        subject = 'Password Reset - Bookutu'
        message = f'''
        Hi {user.first_name},

        You requested a password reset for your Bookutu account.

        Use this token to reset your password: {token}

        This token will expire in 24 hours.

        If you didn't request this, please ignore this email.

        Best regards,
        Bookutu Team
        '''

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class PasswordResetConfirmView(APIView):
    """
    Password reset confirmation endpoint
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                reset_token = PasswordResetToken.objects.get(
                    token=token,
                    is_used=False
                )

                if reset_token.is_expired():
                    return Response(
                        {'error': 'Token has expired.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Reset password
                user = reset_token.user
                user.set_password(new_password)
                user.save()

                # Mark token as used
                reset_token.is_used = True
                reset_token.save()

                return Response({'message': 'Password reset successful.'})

            except PasswordResetToken.DoesNotExist:
                return Response(
                    {'error': 'Invalid token.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSessionsView(generics.ListAPIView):
    """
    List user's active sessions
    """
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSession.objects.filter(
            user=self.request.user,
            is_active=True
        )


class LogoutView(APIView):
    """
    Logout endpoint - deactivate current session
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Deactivate current session
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.filter(
                user=request.user,
                session_key=session_key
            ).update(is_active=False)

        return Response({'message': 'Logged out successfully.'})


class LogoutAllView(APIView):
    """
    Logout from all devices
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Deactivate all user sessions
        UserSession.objects.filter(user=request.user).update(is_active=False)

        return Response({'message': 'Logged out from all devices.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_email(request):
    """
    Email verification endpoint
    """
    # This would typically involve sending a verification email
    # and then verifying the token sent back
    user = request.user
    user.is_verified = True
    user.save()

    return Response({'message': 'Email verified successfully.'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_data(request):
    """
    Get dashboard data based on user type
    """
    user = request.user

    if user.user_type == 'COMPANY_STAFF':
        # Return company dashboard data
        from bookings.models import Booking
        from trips.models import Trip

        today_bookings = Booking.objects.filter(
            company=user.company,
            created_at__date=timezone.now().date()
        ).count()

        upcoming_trips = Trip.objects.filter(
            company=user.company,
            departure_date__gte=timezone.now().date(),
            status='SCHEDULED'
        ).count()

        return Response({
            'user_type': 'company_staff',
            'company_name': user.company.name,
            'today_bookings': today_bookings,
            'upcoming_trips': upcoming_trips,
            'company_status': user.company.status
        })

    elif user.user_type == 'SUPER_ADMIN':
        # Return super admin dashboard data
        from companies.models import Company
        from bookings.models import Booking

        total_companies = Company.objects.count()
        active_companies = Company.objects.filter(status='ACTIVE').count()
        today_bookings = Booking.objects.filter(
            created_at__date=timezone.now().date()
        ).count()

        return Response({
            'user_type': 'super_admin',
            'total_companies': total_companies,
            'active_companies': active_companies,
            'today_bookings': today_bookings
        })

    return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)