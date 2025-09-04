from django.contrib import admin
from .models import Category, EventRegistration, Post, Photo, Blog, Event
from django.utils.html import format_html
from django.contrib.auth.models import User
from accounts.models import CustomUserProfile  # Assuming this is where the user_type field is
from .forms import BlogForm
from tinymce.widgets import TinyMCE
from django.db import models

# Custom filter for users with user_type='photographer'
class PhotographerUserFilter(admin.SimpleListFilter):
    title = 'Photographer'  # This is the title displayed in the filter
    parameter_name = 'user'  # This is the URL query parameter used for filtering

    def lookups(self, request, model_admin):
        # Return only photographers in the filter options
        photographers = User.objects.filter(customuserprofile__user_type='photographer')
        # Ensure it shows the full name or username
        return [(user.id, user.get_full_name() or user.username) for user in photographers]

    def queryset(self, request, queryset):
        # If a specific photographer is selected, filter the queryset accordingly
        if self.value():
            return queryset.filter(user__id=self.value())
        return queryset


# Category Admin
class ShowCategory(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('title', 'description', 'display_image')
    search_fields = Category.SearchableFields

    def display_image(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" height="50" />'.format(obj.thumbnail.url))
        else:
            return 'No banner available'

    display_image.short_description = 'Category Banner'


# Post Admin
class ShowPost(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('title', 'description', 'category', 'display_image', 'is_published', 'is_feature')
    search_fields = Post.SearchableFields
    list_filter = Post.FilterFields

    def display_image(self, obj):
        if obj.banner:
            return format_html('<img src="{}" height="50" />'.format(obj.banner.url))
        else:
            return 'No banner available'

    display_image.short_description = 'Post Banner'


# Photo Admin
class ShowPhoto(admin.ModelAdmin):
    list_display = ('title', 'category', 'user', 'uploaded_at', 'total_views', 'display_image')
    search_fields = ('title', 'description', 'user__username')
    list_filter = ('category', PhotographerUserFilter)  # Use custom filter for photographers
    readonly_fields = ('total_views',)  # Mark total_views as read-only

    def display_image(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" height="50" />'.format(obj.thumbnail.url))
        else:
            return 'No thumbnail available'

    display_image.short_description = 'Photo Thumbnail'

    # Ensure that only photos by photographers are displayed
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__customuserprofile__user_type='photographer')

    # Ensure that only photographers are selectable in the user field
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Restrict user choices to photographers only
        form.base_fields['user'].queryset = User.objects.filter(customuserprofile__user_type='photographer')
        return form

class ShowBlog(admin.ModelAdmin):
    form = BlogForm
    exclude = ('slug',)
    list_display = ('title', 'user', 'display_banner', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at',)

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})}
    }

    def display_banner(self, obj):
        if obj.banner:
            return format_html('<img src="{}" height="50" />'.format(obj.banner.url))
        else:
            return 'No banner available'
    display_banner.short_description = 'Blog Banner'

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')  # was: ('title', 'start_date', 'end_date', 'active', 'created_at')
    list_filter = ('created_at',)  # was: ('active', 'start_date', 'end_date')
    search_fields = ('title', 'description')

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'created_at')
    list_filter = ('event',)        

# Registering Models
admin.site.register(Category, ShowCategory)
admin.site.register(Post, ShowPost)
admin.site.register(Photo, ShowPhoto)
admin.site.register(Blog, ShowBlog)
