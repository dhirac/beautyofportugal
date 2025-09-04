
from django.urls import path
from . import views



urlpatterns = [
    path('register/',views.boplogin,name="register"),
    path('signup/photographer/',views.signup_photographer,name="signup_photographer"),
    path('signup/',views.signup,name="signup"),
    path('logout/',views.boplogout,name="logout"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
] 


