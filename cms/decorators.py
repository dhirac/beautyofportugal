from django.http import HttpResponseForbidden
from accounts.models import CustomUserProfile

def user_type_required(user_type):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            try:
                user_profile = CustomUserProfile.objects.get(user=request.user)
                if user_profile.user_type != user_type:
                    return HttpResponseForbidden("You do not have permission to access this page.")
            except CustomUserProfile.DoesNotExist:
                return HttpResponseForbidden("User profile does not exist.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
