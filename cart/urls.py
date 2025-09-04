from django.urls import path
from . import views

urlpatterns = [
    path('addCart/', views.add_to_cart, name='addCart'),
    path('cart/', views.view_cart, name='cart'),
    path('updateCart/', views.update_cart, name='updateCart'),
    path('deleteCart/', views.remove_item, name='deleteCart'),
    path('billingDetails/', views.billing_details, name='billingDetails'),
    path('payment/', views.stripe_payment, name='payment'),
    path('success/', views.success, name='success'),
   # path('cancel/', views.cancel, name='cancel'),
    
]
