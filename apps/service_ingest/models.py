"""Models for external service telemetry ingest."""

import uuid

from django.db import models

try:
    from ansible_base.lib.abstract_models import CommonModel
except ImportError:
    class CommonModel(models.Model):
        created = models.DateTimeField(auto_now_add=True)
        modified = models.DateTimeField(auto_now=True)

        class Meta:
            abstract = True


def _uuid4_str() -> str:
    return str(uuid.uuid4())


class ExternalEvent(CommonModel):
    """Telemetry payload received from an external AAP service."""

    PAYLOAD_TYPE_CHOICES = [
        ("batch", "Batch"),
        ("event", "Event"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    service_name = models.CharField(max_length=100)
    segment_event_name = models.CharField(max_length=255)
    payload_type = models.CharField(max_length=10, choices=PAYLOAD_TYPE_CHOICES)

    # Batch: time window covered by this payload
    collection_start = models.DateTimeField(null=True, blank=True)
    collection_end = models.DateTimeField(null=True, blank=True)

    # Per-event: when the event occurred on the sender
    event_timestamp = models.DateTimeField(null=True, blank=True)

    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    segment_anonymous_id = models.CharField(max_length=64, default=_uuid4_str)
    retry_count = models.IntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["service_name", "status"]),
            models.Index(fields=["payload_type", "status", "created"]),
        ]

    def __str__(self) -> str:
        return f"{self.service_name} {self.payload_type} [{self.status}] @ {self.created}"
