import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as simplejwt_settings
from rest_framework_simplejwt.tokens import RefreshToken

from common.enums import UserType
from common.permissions import IsCompanyStaff

from .emails import send_company_admin_invite
from .serializers import (
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    PasswordSetupSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    StaffRegisterSerializer,
    UserSerializer,
)

User = get_user_model()


def _build_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def _hash_setup_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def _check_user_access(actor, target_user):
    """SUPER_ADMIN can manage anyone. COMPANY_STAFF can manage any passenger
    account plus staff belonging to their own company (not other companies,
    not super admins)."""
    if actor.user_type == 'SUPER_ADMIN':
        return True
    if target_user.user_type == 'PASSENGER':
        return True
    if target_user.user_type == 'COMPANY_STAFF':
        return actor.user_type == 'COMPANY_STAFF' and actor.company_id == target_user.company_id
    return False


class AuthViewSet(viewsets.ViewSet):
    throttle_scope = None

    def get_permissions(self):
        if self.action in {'login', 'refresh', 'logout', 'register', 'bootstrap_super_admin', 'password_setup', 'set_password'}:
            return [AllowAny()]
        if self.action in {'register_staff', 'users', 'retrieve', 'update', 'partial_update', 'destroy'}:
            return [IsAuthenticated(), IsCompanyStaff()]
        if self.action in {'me', 'update_me', 'change_password'}:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False, methods=['post'], permission_classes=[AllowAny],
        throttle_classes=[ScopedRateThrottle], throttle_scope='login', url_path='login',
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        if not user:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'user': UserSerializer(user).data, **_build_tokens(user)})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='refresh')
    def refresh(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
        except TokenError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

        data = {'access': str(token.access_token)}
        if simplejwt_settings.ROTATE_REFRESH_TOKENS:
            if simplejwt_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    token.blacklist()
                except AttributeError:
                    pass
            token.set_jti()
            token.set_exp()
            token.set_iat()
            data['refresh'] = str(token)
        return Response(data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='logout')
    def logout(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass
        return Response({'detail': 'Logged out successfully.'})

    @action(
        detail=False, methods=['post'], permission_classes=[AllowAny],
        throttle_classes=[ScopedRateThrottle], throttle_scope='register', url_path='register',
    )
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'user': UserSerializer(user).data, **_build_tokens(user)}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='bootstrap-super-admin')
    def bootstrap_super_admin(self, request):
        payload = request.data.copy()
        payload['user_type'] = UserType.SUPER_ADMIN
        payload['is_staff'] = True
        payload['is_superuser'] = True
        if User.objects.filter(user_type=UserType.SUPER_ADMIN).exists():
            return Response({'detail': 'Super admin already exists.'}, status=status.HTTP_409_CONFLICT)
        serializer = RegisterSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.user_type = UserType.SUPER_ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=['user_type', 'is_staff', 'is_superuser'])
        return Response({'user': UserSerializer(user).data, **_build_tokens(user)}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='password-setup/(?P<token>[^/.]+)')
    def password_setup(self, request, token=None):
        exists = User.objects.filter(password_setup_token_hash=_hash_setup_token(token)).exists()
        return Response({'token': token, 'valid': exists})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='set-password')
    def set_password(self, request):
        serializer = PasswordSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']

        token_hash = _hash_setup_token(token)
        user = User.objects.filter(password_setup_token_hash=token_hash).first()
        is_valid = (
            user is not None
            and user.password_setup_token_hash
            and user.password_setup_token_expires_at
            and timezone.now() <= user.password_setup_token_expires_at
            and user.password_setup_token_hash == token_hash
        )
        if not is_valid:
            return Response({'detail': 'Invalid or expired setup token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.password_setup_token_hash = None
        user.password_setup_token_expires_at = None
        user.is_verified = True
        if serializer.validated_data.get('first_name'):
            user.first_name = serializer.validated_data['first_name']
        if serializer.validated_data.get('last_name'):
            user.last_name = serializer.validated_data['last_name']
        if serializer.validated_data.get('phone_number'):
            user.phone_number = serializer.validated_data['phone_number']
        user.save()

        return Response({
            'message': 'Password set successfully',
            'user': UserSerializer(user).data,
            **_build_tokens(user),
        })

    @action(detail=False, methods=['post'], url_path='register/staff')
    def register_staff(self, request):
        data = dict(request.data)
        if request.user.user_type == 'COMPANY_STAFF':
            data['company_id'] = request.user.company_id
        serializer = StaffRegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        company = serializer.validated_data['company']
        email = serializer.validated_data['email']

        existing = User.objects.filter(email=email).first()
        if existing:
            if existing.user_type != UserType.COMPANY_STAFF:
                return Response({'detail': 'This email is already used by another Bookutu account.'}, status=status.HTTP_409_CONFLICT)
            if existing.is_verified:
                return Response({'detail': 'This company admin already has an active account.'}, status=status.HTTP_409_CONFLICT)

        raw_token = secrets.token_hex(32)
        token_hash = _hash_setup_token(raw_token)
        expires_at = timezone.now() + timedelta(hours=24)
        invited_at = timezone.now()

        if existing:
            user = existing
            user.first_name = serializer.validated_data.get('first_name') or user.first_name
            user.last_name = serializer.validated_data.get('last_name') or user.last_name
            user.phone_number = serializer.validated_data.get('phone_number') or user.phone_number
            user.company = company
            user.is_active = True
            user.password_setup_token_hash = token_hash
            user.password_setup_token_expires_at = expires_at
            user.invited_at = invited_at
            user.set_unusable_password()
            user.save()
        else:
            user = User(
                email=email,
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                phone_number=serializer.validated_data.get('phone_number', ''),
                company=company,
                user_type=UserType.COMPANY_STAFF,
                is_active=True,
                is_verified=False,
                password_setup_token_hash=token_hash,
                password_setup_token_expires_at=expires_at,
                invited_at=invited_at,
            )
            user.set_unusable_password()
            user.save()

        setup_base_url = settings.DASHBOARD_BASE_URL.rstrip('/')
        setup_url = f'{setup_base_url}/set-password?token={raw_token}'
        delivery = send_company_admin_invite(to=email, company_name=company.name, setup_url=setup_url)

        return Response({
            'message': 'Company admin invite created successfully',
            'invite': {
                'email': user.email,
                'company_id': company.id,
                'company_name': company.name,
                'expires_at': expires_at,
                'delivery_mode': delivery['mode'],
            },
            'setup_url': setup_url if settings.DEBUG else None,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='users')
    def users(self, request):
        queryset = User.objects.all().order_by('-created_at')
        user_type = request.query_params.get('userType')
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        if request.user.user_type == 'COMPANY_STAFF':
            queryset = queryset.filter(
                Q(user_type='PASSENGER') | Q(user_type='COMPANY_STAFF', company_id=request.user.company_id)
            )

        serializer = UserSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        if not _check_user_access(request.user, user):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'data': UserSerializer(user).data})

    def update(self, request, pk=None):
        return self._update_user(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._update_user(request, pk, partial=True)

    def _update_user(self, request, pk, partial):
        user = get_object_or_404(User, pk=pk)
        if not _check_user_access(request.user, user):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': UserSerializer(user).data})

    def destroy(self, request, pk=None):
        if str(request.user.id) == str(pk):
            return Response({'detail': 'You cannot delete your own account.'}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, pk=pk)
        if not _check_user_access(request.user, user):
            return Response({'detail': 'Insufficient permissions.'}, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=['patch'], url_path='me')
    def update_me(self, request):
        serializer = ProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='me/password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        return Response({'detail': 'Password changed successfully.'})
