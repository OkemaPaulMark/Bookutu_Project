from rest_framework import serializers

from companies.models import Company

from .models import Delivery


class _StaffSummarySerializer(serializers.Serializer):
    id = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class DeliverySerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(source='company', queryset=Company.objects.all(), required=False)
    registered_by = _StaffSummarySerializer(read_only=True)
    picked_up_by = _StaffSummarySerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = [
            'id', 'tracking_number', 'company_id',
            'sender_name', 'sender_phone', 'receiver_name', 'receiver_phone',
            'origin_terminal', 'destination_terminal', 'package_description', 'fee',
            'status', 'registered_by', 'picked_up_by', 'picked_up_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'tracking_number', 'status', 'picked_up_at', 'created_at', 'updated_at']
