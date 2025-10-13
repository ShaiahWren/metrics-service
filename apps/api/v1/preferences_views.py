"""
ViewSet for dynamic preferences API.
"""
from ansible_base.lib.utils.views.django_app_api import AnsibleBaseDjangoAppApiView
from ansible_base.oauth2_provider.permissions import OAuth2ScopePermission
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from dynamic_preferences.registries import global_preferences_registry

from .preferences_serializers import PreferenceSerializer, PreferenceUpdateSerializer


@extend_schema_view(
    list=extend_schema(summary="List all dynamic preferences", tags=["preferences"]),
)
class PreferencesViewSet(AnsibleBaseDjangoAppApiView, viewsets.ViewSet):
    """
    ViewSet for managing dynamic preferences.
    
    Supports runtime configuration updates without service restart.
    """
    
    permission_classes = [OAuth2ScopePermission]
    
    def _get_preference_data(self, pref_instance, manager):
        """Helper to serialize a preference instance."""
        key = f"{pref_instance.section.name}__{pref_instance.name}"
        current_value = manager[key]
        
        return {
            'section': pref_instance.section.name,
            'name': pref_instance.name,
            'value': current_value,
            'default': pref_instance.default,
            'verbose_name': pref_instance.verbose_name,
            'help_text': pref_instance.help_text,
        }
    
    @extend_schema(
        summary="List all preferences",
        responses={200: PreferenceSerializer(many=True)},
    )
    def list(self, request):
        """List all dynamic preferences with current values."""
        manager = global_preferences_registry.manager()
        preferences = global_preferences_registry.preferences()
        
        data = [self._get_preference_data(pref, manager) for pref in preferences]
        
        serializer = PreferenceSerializer(data, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get a specific preference",
        responses={200: PreferenceSerializer},
    )
    def retrieve(self, request, pk=None):
        """
        Get a specific preference by key.
        
        Key format: section__name (e.g., 'dispatcherd__workers')
        """
        try:
            section, name = pk.split('__', 1)
        except ValueError:
            return Response(
                {'error': 'Invalid key format. Use: section__name (e.g., dispatcherd__workers)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pref = global_preferences_registry.get(section=section, name=name)
            manager = global_preferences_registry.manager()
            
            data = self._get_preference_data(pref, manager)
            serializer = PreferenceSerializer(data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Preference not found: {str(e)}'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Update a preference value",
        request=PreferenceUpdateSerializer,
        responses={200: PreferenceSerializer},
    )
    def update(self, request, pk=None):
        """
        Update a preference value.
        
        Key format: section__name (e.g., 'dispatcherd__workers')
        """
        try:
            section, name = pk.split('__', 1)
        except ValueError:
            return Response(
                {'error': 'Invalid key format. Use: section__name (e.g., dispatcherd__workers)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PreferenceUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            manager = global_preferences_registry.manager()
            
            # Update the preference (validation happens here)
            manager[pk] = serializer.validated_data['value']
            
            # Return updated preference
            pref = global_preferences_registry.get(section=section, name=name)
            data = self._get_preference_data(pref, manager)
            response_serializer = PreferenceSerializer(data)
            
            return Response(response_serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': f'Validation error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to update preference: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Reset preference to default",
        responses={200: PreferenceSerializer},
    )
    def destroy(self, request, pk=None):
        """
        Reset a preference to its default value.
        
        Key format: section__name (e.g., 'dispatcherd__workers')
        """
        try:
            section, name = pk.split('__', 1)
        except ValueError:
            return Response(
                {'error': 'Invalid key format. Use: section__name (e.g., dispatcherd__workers)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pref = global_preferences_registry.get(section=section, name=name)
            manager = global_preferences_registry.manager()
            
            # Reset to default by setting the default value
            manager[pk] = pref.default
            
            data = self._get_preference_data(pref, manager)
            serializer = PreferenceSerializer(data)
            
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to reset preference: {str(e)}'},
                status=status.HTTP_404_NOT_FOUND
            )
