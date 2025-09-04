from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import CustomUserProfile, BopCommission
from .models import LoginAttempt


class CustomUserProfileInline(admin.StackedInline):
    model = CustomUserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'



class UserAdmin(BaseUserAdmin):
    inlines = (CustomUserProfileInline,)

    # Add a list filter for user type
    list_filter = BaseUserAdmin.list_filter + ('customuserprofile__user_type',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('customuserprofile')  # Optimize for related profile access

class BopCommissionAdmin(admin.ModelAdmin):
    list_display = ['commission_percentage']

    def has_add_permission(self, request):
        # Prevent adding more than one global commission
        if BopCommission.objects.exists():
            return False
        return True
    
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'ip_address', 'success', 'timestamp')
    list_filter = ('success', 'timestamp')
    search_fields = ('username', 'ip_address')

# Register the BopCommission model
admin.site.register(BopCommission, BopCommissionAdmin)
admin.site.register(LoginAttempt, LoginAttemptAdmin)

# Unregister the original User admin
admin.site.unregister(User)
# Register the new User admin with the inline profile
admin.site.register(User, UserAdmin)

