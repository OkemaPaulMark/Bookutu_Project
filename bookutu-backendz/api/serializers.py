from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import PassengerProfile

User = get_user_model()

class MobileRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for mobile app user registration.
    Matches what the Flutter app sends: names, email, phone, password(s),
    and optionally date_of_birth / gender.
    """
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=False, allow_blank=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True, write_only=True)
    gender = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "confirm_password", "first_name",
            "last_name", "phone_number", "date_of_birth", "gender",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        dob = validated_data.pop("date_of_birth", None)
        gender = (validated_data.pop("gender", "") or "").upper()[:1]
        if not validated_data.get("username"):
            validated_data.pop("username", None)

        validated_data['user_type'] = 'PASSENGER'
        user = User.objects.create_user(**validated_data)

        profile, _ = PassengerProfile.objects.get_or_create(user=user)
        if dob:
            profile.date_of_birth = dob
        if gender in ("M", "F", "O"):
            profile.gender = gender
        profile.save()

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


class MobileLoginSerializer(serializers.Serializer):
    """
    Custom JWT token serializer for mobile app login.
    Accepts either "email" (what the Flutter app sends) or "username".
    """
    email = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        identifier = (attrs.get("email") or attrs.get("username") or "").strip()
        password = attrs.get("password")

        if not identifier or not password:
            raise serializers.ValidationError({"non_field_errors": ["Email and password are required."]})

        user = authenticate(username=identifier, password=password)
        if not user:
            raise serializers.ValidationError({"non_field_errors": ["Invalid email or password."]})
        if not user.is_active:
            raise serializers.ValidationError({"non_field_errors": ["User account is disabled."]})

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh_token = RefreshToken.for_user(user)

        data = {
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
        }
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
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