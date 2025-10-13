"""
Dynamic preferences for Metrics Service.
Follows AAP patterns for runtime-configurable settings.
"""
from dynamic_preferences.types import IntegerPreference, StringPreference, Section
from dynamic_preferences.registries import global_preferences_registry


# Define sections for organizing preferences
dispatcherd = Section('dispatcherd', verbose_name='Dispatcherd Configuration')
cors = Section('cors', verbose_name='CORS Configuration')
oauth2 = Section('oauth2', verbose_name='OAuth2 Configuration')
jwt = Section('jwt', verbose_name='JWT Configuration')


# ========== DISPATCHERD PREFERENCES ==========

@global_preferences_registry.register
class WorkersPreference(IntegerPreference):
    """Number of dispatcherd worker processes."""
    
    section = dispatcherd
    name = 'workers'
    default = 4
    required = False
    verbose_name = 'Worker Count'
    help_text = 'Number of worker processes for task processing'
    
    def validate(self, value):
        """Validate worker count is within acceptable range."""
        if value < 1:
            raise ValueError('Workers must be at least 1')
        if value > 100:
            raise ValueError('Workers cannot exceed 100 (resource limit)')
        return value


@global_preferences_registry.register
class MaxTasksPreference(IntegerPreference):
    """Maximum number of tasks in queue."""
    
    section = dispatcherd
    name = 'max_tasks'
    default = 100
    required = False
    verbose_name = 'Maximum Tasks'
    help_text = 'Maximum number of tasks that can be queued'
    
    def validate(self, value):
        """Validate max tasks is within acceptable range."""
        if value < 1:
            raise ValueError('Max tasks must be at least 1')
        if value > 10000:
            raise ValueError('Max tasks cannot exceed 10000 (resource limit)')
        return value


@global_preferences_registry.register
class TimeoutPreference(IntegerPreference):
    """Task execution timeout in seconds."""
    
    section = dispatcherd
    name = 'timeout'
    default = 3600
    required = False
    verbose_name = 'Task Timeout'
    help_text = 'Maximum time in seconds for task execution'
    
    def validate(self, value):
        """Validate timeout is within acceptable range."""
        if value < 1:
            raise ValueError('Timeout must be at least 1 second')
        if value > 86400:  # 24 hours
            raise ValueError('Timeout cannot exceed 86400 seconds (24 hours)')
        return value


# ========== CORS PREFERENCES ==========

@global_preferences_registry.register
class AllowedOriginsPreference(StringPreference):
    """CORS allowed origins (comma-separated)."""
    
    section = cors
    name = 'allowed_origins'
    default = 'http://localhost:3000,http://127.0.0.1:3000'
    required = False
    verbose_name = 'Allowed Origins'
    help_text = 'Comma-separated list of allowed CORS origins'
    
    def validate(self, value):
        """Validate origins format."""
        if not value:
            raise ValueError('At least one origin must be specified')
        # Basic validation - each origin should start with http:// or https://
        origins = [o.strip() for o in value.split(',')]
        for origin in origins:
            if not origin.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid origin format: {origin}. Must start with http:// or https://')
        return value


# ========== OAUTH2 PREFERENCES ==========

@global_preferences_registry.register
class AccessTokenExpirePreference(IntegerPreference):
    """OAuth2 access token expiration in seconds."""
    
    section = oauth2
    name = 'access_token_expire'
    default = 3600
    required = False
    verbose_name = 'Access Token Expiration'
    help_text = 'Access token lifetime in seconds'
    
    def validate(self, value):
        """Validate token expiration is reasonable."""
        if value < 300:  # 5 minutes minimum
            raise ValueError('Access token expiration must be at least 300 seconds (5 minutes)')
        if value > 604800:  # 7 days maximum
            raise ValueError('Access token expiration cannot exceed 604800 seconds (7 days)')
        return value


# ========== JWT PREFERENCES ==========

@global_preferences_registry.register
class JWTExpirationPreference(IntegerPreference):
    """JWT token expiration in seconds."""
    
    section = jwt
    name = 'expiration'
    default = 3600
    required = False
    verbose_name = 'JWT Expiration'
    help_text = 'JWT token lifetime in seconds'
    
    def validate(self, value):
        """Validate JWT expiration is reasonable."""
        if value < 300:  # 5 minutes minimum
            raise ValueError('JWT expiration must be at least 300 seconds (5 minutes)')
        if value > 604800:  # 7 days maximum
            raise ValueError('JWT expiration cannot exceed 604800 seconds (7 days)')
        return value
