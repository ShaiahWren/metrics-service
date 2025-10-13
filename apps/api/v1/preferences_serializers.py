"""
Serializers for dynamic preferences API.
"""
from rest_framework import serializers


class PreferenceSerializer(serializers.Serializer):
    """Serializer for a single preference."""
    
    section = serializers.CharField(read_only=True, help_text="Preference section (e.g., 'dispatcherd')")
    name = serializers.CharField(read_only=True, help_text="Preference name (e.g., 'workers')")
    value = serializers.JSONField(help_text="Current preference value")
    default = serializers.JSONField(read_only=True, help_text="Default value")
    verbose_name = serializers.CharField(read_only=True, help_text="Human-readable name")
    help_text = serializers.CharField(read_only=True, help_text="Description of this preference")
    

class PreferenceUpdateSerializer(serializers.Serializer):
    """Serializer for updating a preference value."""
    
    value = serializers.JSONField(required=True, help_text="New value for the preference")
