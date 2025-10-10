from rest_framework import serializers
from .models import Advert

class AdvertSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # Return full URL

    class Meta:
        model = Advert
        fields = ['id', 'title', 'description', 'image', 'link_url', 'is_active', 'start_date', 'end_date']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return ''
