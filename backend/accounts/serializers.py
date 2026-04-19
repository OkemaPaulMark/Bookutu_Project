from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import PassengerProfile, UserSession
from companies.models import Company

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user information
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user information to token response
        data.update({
            'user': {
                'id': self.user.id,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'user_type': self.user.user_type,
                'company_id': self.user.company.id if self.user.company else None,
                'company_name': self.user.company.name if self.user.company else None,
                'is_verified': self.user.is_verified,
            }
        })
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User registration serializer
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_passenger(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', '')
        )
        return user


class CompanyStaffRegistrationSerializer(serializers.ModelSerializer):
    """
    Company staff registration serializer (for super admin use)
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    company_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password', 'password_confirm', 'company_id')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Validate company exists
        try:
            company = Company.objects.get(id=attrs['company_id'])
            attrs['company'] = company
        except Company.DoesNotExist:
            raise serializers.ValidationError("Invalid company ID")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        company = validated_data.pop('company')
        validated_data.pop('company_id')
        
        user = User.objects.create_company_staff(
            email=validated_data['email'],
            company=company,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', '')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile serializer
    """
    passenger_profile = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 
                 'user_type', 'company_name', 'is_verified', 'date_joined', 'passenger_profile')
        read_only_fields = ('id', 'email', 'user_type', 'company_name', 'is_verified', 'date_joined')
    
    def get_passenger_profile(self, obj):
        if obj.user_type == 'PASSENGER' and hasattr(obj, 'passenger_profile'):
            return PassengerProfileSerializer(obj.passenger_profile).data
        return None


class PassengerProfileSerializer(serializers.ModelSerializer):
    """
    Passenger profile serializer
    """
    class Meta:
        model = PassengerProfile
        fields = ('date_of_birth', 'gender', 'emergency_contact_name', 'emergency_contact_phone',
                 'preferred_language', 'preferred_seat_type', 'loyalty_points', 'total_bookings')
        read_only_fields = ('loyalty_points', 'total_bookings')


class PasswordChangeSerializer(serializers.Serializer):
    """
    Password change serializer
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Password reset request serializer
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Password reset confirmation serializer
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """
    User session serializer
    """
    class Meta:
        model = UserSession
        fields = ('id', 'device_type', 'ip_address', 'created_at', 'last_activity', 'is_active')
        read_only_fields = ('id', 'created_at', 'last_activity')
