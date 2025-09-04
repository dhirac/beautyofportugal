from .models import CustomUserProfile

def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = CustomUserProfile.objects.get(user=request.user)
        except CustomUserProfile.DoesNotExist:
            profile = None
        return {'user_profile': profile}
    return {}
