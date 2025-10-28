from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import PassengerProfile

User = get_user_model()

class MobileRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for mobile app user registration
    """
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "confirm_password"
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        # Create user with passenger user type
        validated_data['user_type'] = 'PASSENGER'
        user = User.objects.create_user(**validated_data)

        # Create passenger profile (only if it doesn't exist)
        PassengerProfile.objects.get_or_create(user=user)

        return user

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return User.objects.create_user(**validated_data)


class MobileLoginSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer for mobile app login
    """
    def validate(self, attrs):
        # Allow login with username instead of email
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError({"non_field_errors": ["Invalid username or password."]})
            if not user.is_active:
                raise serializers.ValidationError({"non_field_errors": ["User account is disabled."]})

            # Set username for parent class (already set)
            attrs['username'] = username
        else:
            raise serializers.ValidationError({"non_field_errors": ["Username and password are required."]})

        data = super().validate(attrs)

        # Add user info to response
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_type": user.user_type,
            "is_verified": user.is_verified
        }

        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        user = authenticate(username=attrs.get("username"), password=attrs.get("password"))
        if not user:
            raise serializers.ValidationError({"non_field_errors": ["Invalid username or password."]})
        data = super().validate(attrs)
        data["user"] = {"id": user.id, "username": user.username, "email": user.email}
        return data


from rest_framework import serializers
from trips.models import Trip

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = (
            'id', 'route', 'bus', 'departure_date', 'departure_time', 'arrival_time',
            'base_fare', 'status', 'driver_name', 'driver_phone',
            'conductor_name', 'conductor_phone', 'notes'
        )
        read_only_fields = ('id',)