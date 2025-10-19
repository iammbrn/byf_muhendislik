from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """User management - Add users (admins use AdminUserProxy section)"""
    list_display = ('username', 'email', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Bilgiler', {
            'fields': ('user_type', 'phone', 'email_verified')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'first_name', 'last_name'),
        }),
    )
    
    def has_module_permission(self, request):
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_superuser  # Allow superusers to add users
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_type')
    list_filter = ('user__user_type',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)
    
    def get_user_type(self, obj):
        return obj.user.get_user_type_display()
    get_user_type.short_description = 'Tip'
    
    def has_module_permission(self, request):
        return request.user.is_superuser