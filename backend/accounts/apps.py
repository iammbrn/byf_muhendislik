from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Hesap Yönetimi'
    
    def ready(self):
        # Import admin modules to ensure they are registered
        import accounts.admin
        import accounts.admin_management