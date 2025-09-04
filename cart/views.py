from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, CartItem
from django.http import JsonResponse
from cms.models import Photo
from cart.models import CartItem
from django.views.decorators.http import require_POST
import json
from .forms import BillingForm
from .models import BillingDetail, Orders, OrderItem
from django.db.models import Sum
from decimal import Decimal, InvalidOperation
import traceback
from django.db import IntegrityError
import stripe
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


@require_POST
def add_to_cart(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Parse the request body to get the photo_id
            data = json.loads(request.body)
            photo_id = data.get('photo_id')

            if not photo_id:
                return JsonResponse({'error': 'Photo ID not provided'}, status=400)

            # Retrieve or create the user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)

            try:
                # Get the photo object
                photo = Photo.objects.get(id=photo_id)

                # Log the price for debugging
                photo_price_decimal = Decimal(str(photo.price))  # Ensure the price is in Decimal format

                # Check if the item is already in the cart
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=photo)

                if created:
                    # If the item was created, set the price
                    cart_item.price = photo_price_decimal
                else:
                    # If the item already exists, increase the quantity
                    cart_item.quantity += 1

                # Save the cart item with the price
                cart_item.save()

                # Update total quantity in the cart
                total_quantity = CartItem.objects.filter(cart=cart).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

                return JsonResponse({'cart_count': total_quantity, 'message': 'Product added to cart successfully!'})

            except Photo.DoesNotExist:
                return JsonResponse({'error': 'Photo not found'}, status=404)

            except Exception as e:
                print(f"Error occurred: {e}")
                return JsonResponse({'error': str(e)}, status=500)

    

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.items.all()
    total = sum(item.get_total_price() for item in items)
    return render(request, 'view_cart.html', {'items': items, 'total': total})


@require_POST
def update_cart(request):
    data = json.loads(request.body)
    item_id = data.get('id')
    quantity = data.get('quantity')

    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.quantity = quantity
        cart_item.save()

        # Update total quantity in the cart
        total_quantity = CartItem.objects.filter(cart=cart_item.cart).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

        return JsonResponse({'cart_count': total_quantity, 'message': 'Quantity updated successfully!'})

    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Cart item not found'}, status=404)

@require_POST
def remove_item(request):
    try:
        item_id = json.loads(request.body).get('id')
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()

        # Get the updated cart count
        updated_cart_count = CartItem.objects.filter(cart=cart_item.cart).aggregate(total=Sum('quantity'))['total'] or 0

        return JsonResponse({'cart_count': updated_cart_count}, status=200)
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Cart item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def billing_details(request):
    # Fetch billing details if they exist
    try:
        billing_details = BillingDetail.objects.get(user=request.user)
    except BillingDetail.DoesNotExist:
        billing_details = None

    if request.method == 'POST':
        form = BillingForm(request.POST, instance=billing_details)
        if form.is_valid():
            billing = form.save(commit=False)
            billing.user = request.user
            billing.save()

            return JsonResponse({'success': True, 'message': 'Shipping details saved successfully.'})

        else:
            return JsonResponse({'success': False, 'errors': form.errors})          

    else:
        form = BillingForm(instance=billing_details)

    return render(request, 'billing_details.html', {'form': form})

stripe.api_key = settings.STRIPE_SECRET_KEY
DOMAIN = "http://127.0.0.1:1234/"
def stripe_payment(request):
    billing_details = BillingDetail.objects.filter(user=request.user).first()
    if not billing_details:
        return redirect('billing_details')  # Ensure billing details exist

    # Fetch cart items
    cart_items = CartItem.objects.filter(cart__user=request.user)
    total_amount = sum(item.get_total_price() for item in cart_items)

    if total_amount <= 0:
        return render(request, 'empty_cart.html')  # Handle empty cart

    # Create a checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': item.product.title,
                    },
                    'unit_amount': int(item.price * 100),  # Amount in cents
                },
                'quantity': item.quantity,
            } for item in cart_items
        ],
        mode='payment',
        success_url=f"{DOMAIN}/success/?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=request.build_absolute_uri('/cancel/'),
    )

    return redirect(session.url)


def success(request):
    stripe_payment_id = request.GET.get('session_id')
    if not stripe_payment_id:
        return render(request, 'error.html', {'message': 'Session ID is missing.'})

    # Retrieve the session from Stripe
    session = stripe.checkout.Session.retrieve(stripe_payment_id)
    total_amount = session.amount_total / 100  # Convert from cents to euros

    # Retrieve the payment method ID
    payment_method_id = session.payment_intent  # This contains the payment method ID

    # Fetch the user's active cart from the database
    try:
        cart = Cart.objects.get(user=request.user)  
    except Cart.DoesNotExist:
        return render(request, 'error.html', {'message': 'No active cart found.'})

    # Retrieve cart items
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return render(request, 'error.html', {'message': 'No items in cart.'})

    # Calculate total amount from cart items
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    # Retrieve or create billing details
    billing_detail = BillingDetail.objects.get(user=request.user)

    

    # Create the order and store cart items in the order
    order = Orders.objects.create(
        user=request.user,
        billing_detail=billing_detail,
        total_amount=total_amount,
        stripe_payment_id=payment_method_id
    )

    # Create a dictionary to store items grouped by photographer
    photographer_items = {}

    # Create order items based on the cart items
    for item in cart_items:
        product_id = item.product.id  # Assuming `product` is the ForeignKey to Photo
        photo = Photo.objects.get(id=product_id)  # Retrieve the photo instance

        order_item = OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
            photo_owner = photo
        )

        # Add the order item to the respective photographer's list
        photographer = photo.user  # The photographer is the owner of the photo
        if photographer not in photographer_items:
            photographer_items[photographer] = []
        photographer_items[photographer].append(order_item)

    # Delete the cart and its items
    cart_items.delete()  # Clear the cart items
    cart.delete()  # Delete the cart itself

    # Optionally, clear the session cart if you're still using it
    request.session['cart_items'] = []

    send_order_confirmation_email(request.user, order)

    # Send emails to photographers with all items sold to each
    for photographer, items in photographer_items.items():
        send_order_confirmation_to_photographer(photographer, order, items)

    return render(request, 'success.html', {'order': order})



def send_order_confirmation_email(user, order):
    subject = 'Order Confirmation'
    html_message = render_to_string('email_order_confirmation.html', {
        'user': user,
        'order': order,
        'order_items': order.items.all(),  # Assuming you have a related field 'items'
    })
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    # Send mail with plain text and HTML versions
    send_mail(
        subject,                         # Subject
        plain_message,                   # Plain text message (fallback)
        settings.DEFAULT_FROM_EMAIL,     # From email
        [user.email],                    # To email
        html_message=html_message,       # HTML message
        fail_silently=False,
    )
    
def send_order_confirmation_to_photographer(photographer, order, items):
    total_earnings = sum(item.price * item.quantity for item in items)  # Calculate total earnings

    subject = 'New Order for Your Photos!'
    html_message = render_to_string('email_order_confirmation_photo_owner.html', {
        'photographer': photographer,
        'order': order,
        'items': items,
        'total_earnings': total_earnings,  # Pass the total earnings to the template
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [photographer.email],
        html_message=html_message,
        fail_silently=False,
    )
