from django.urls import path

from apps.service_ingest.v1.views import IngestView

app_name = "service_ingest_v1"

urlpatterns = [
    path("events/", IngestView.as_view(), name="events"),
]
