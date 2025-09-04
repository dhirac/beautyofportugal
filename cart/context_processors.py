from django.db import models  # Add this line
from .models import CartItem, Cart

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            # Sum the quantity of all items in the cart
            total_quantity = CartItem.objects.filter(cart=cart).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
            return {'cart_count': total_quantity}
    return {'cart_count': 0}
