from django.db import models

from common.ids import generate_id
from common.models import TimeStampedModel


class Announcement(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=30)
    target_audience = models.CharField(max_length=120)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='announcements')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']


class SystemLog(TimeStampedModel):
    id = models.CharField(primary_key=True, max_length=32, default=generate_id, editable=False)
    action = models.CharField(max_length=120)
    user = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='system_logs')
    target_model = models.CharField(max_length=120, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    ip_address = models.CharField(max_length=120, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'system_logs'
        ordering = ['-created_at']
