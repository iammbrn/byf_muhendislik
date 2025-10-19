from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Çekirdek Uygulama'
    
    def ready(self):
        # Import signals for cache invalidation
        import core.signals