from rest_framework import serializers

from .models import Company, CompanyEarnings


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'verified_at']


STAFF_EDITABLE_COMPANY_FIELDS = (
    'name', 'description', 'email', 'phone_number', 'website',
    'address', 'city', 'state', 'country', 'postal_code',
)


class CompanyEarningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyEarnings
        fields = '__all__'
