from rest_framework import serializers

from common.enums import UserType
from companies.models import Company

from .models import User


class UserSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(read_only=True, allow_null=True)
    company_name = serializers.SerializerMethodField()
    company_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'user_type',
            'is_active',
            'is_verified',
            'created_at',
            'updated_at',
            'company_id',
            'company_name',
            'company_status',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_company_name(self, obj):
        return obj.company.name if obj.company_id else None

    def get_company_status(self, obj):
        return obj.company.status if obj.company_id else None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 'username']

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, user_type=UserType.PASSENGER, **validated_data)


class StaffRegisterSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', queryset=Company.objects.all())
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'company_id']


class PasswordSetupSerializer(serializers.Serializer):
    token = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'username']


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'is_active', 'is_verified']
