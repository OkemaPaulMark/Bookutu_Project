from django.db import models

from common.ids import generate_id
from common.models import TimeStampedModel


class Advert(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField()
    link_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'adverts'
        ordering = ['-created_at']
