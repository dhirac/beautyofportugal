from django.contrib import admin
from .models import Orders, OrderItem
from accounts.models import CustomUserProfile, BopCommission
from django.contrib.auth.models import User


# Custom filter for users with user_type='customer'
class CustomerUserFilter(admin.SimpleListFilter):
    title = 'Customer'  # Title for the filter panel
    parameter_name = 'user'  # The query parameter for the filter

    def lookups(self, request, model_admin):
        # Get users with user_type='customer' for the filter options
        customers = User.objects.filter(customuserprofile__user_type='customer')
        return [(user.id, user.get_full_name() or user.username) for user in customers]

    def queryset(self, request, queryset):
        # If a specific customer is selected, filter the queryset accordingly
        if self.value():
            return queryset.filter(user__id=self.value())
        return queryset


# Inline for OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price', 'photo_owner_full_name')
    readonly_fields = ('photo_owner_full_name',)

    def photo_owner_full_name(self, instance):
        # Fetch the full name of the photo owner (photographer)
        if instance.photo_owner_id:
            user = User.objects.get(id=instance.photo_owner_id)
            return user.get_full_name() or user.username
        return "No Owner"

    photo_owner_full_name.short_description = 'Photographer'


# Orders Admin
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_amount', 'commission_amount', 'final_amount')
    list_filter = (CustomerUserFilter,)  # Add the custom customer filter here
    inlines = [OrderItemInline]

    def commission_amount(self, obj):
        # Calculate the commission for the first item (assuming same photographer)
        if obj.items.exists():
            first_item = obj.items.first()
           
            commission = BopCommission.objects.get()
            commission = round(obj.total_amount * commission.commission_percentage / 100,2)
            return f"€{commission}"
        return 0

    def final_amount(self, obj):
        # Calculate the final amount after deducting the commission
        if obj.items.exists():
            first_item = obj.items.first()
           
            commission = BopCommission.objects.get()
            commission = round(obj.total_amount * commission.commission_percentage / 100,2)
            return f"€{obj.total_amount - commission}"
        return f"€{obj.total_amount}"

    commission_amount.short_description = 'Commission Amount'
    final_amount.short_description = 'Final Amount (After Commission)'


# Register OrdersAdmin with the custom customer filter
admin.site.register(Orders, OrdersAdmin)
