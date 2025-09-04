from asyncio import Event
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from beautyofportugal import settings
from .forms import EventRegistrationForm, ProfileUpdateForm, PhotoEditForm
from .models import Profile, Category, Photo, Blog
from accounts.models import CustomUserProfile
from .forms import PhotoUploadForm
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
import os
from io import BytesIO
from django.db import models
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .decorators import user_type_required
from cart.models import Orders, OrderItem
from accounts.models import BopCommission
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage


# Create your views here.
from django.db.models import Sum, F
@login_required(login_url='register')
def dashboard(request):
     # Retrieve the profile data for the logged-in user
    # Retrieve the profile data for the logged-in user
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    photographer = request.user

    # Fetch all photos uploaded by the photographer
    photographer_photos = Photo.objects.filter(user=photographer)

    # Calculate stats
    total_photos = photographer_photos.count()  # Total photos uploaded by photographer
    total_views = photographer_photos.aggregate(total_views=Sum('total_views'))['total_views'] or 0  # Sum of all photo views

            

    # Pass the profile data to the template
    context = {
        'profile': profile,
        'email': request.user.email,  # Pass the user's email to the template
        'join_date': request.user.date_joined,  # Pass the user's join date
        'total_photos': total_photos,
        'total_views': total_views,

        
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required
def update_profile(request):
    user = request.user
    # get or create the profile for this user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save()  # saves full_name and avatar in Profile
            return redirect('dashboard')
    else:
        form = ProfileUpdateForm(instance=profile, user=user)

    return render(request, 'dashboard/update_profile.html', {'form': form})




@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()  # Saving the photo will trigger the image processing in the model
            return redirect('dashboard')  # Redirect after successful upload
    else:
        form = PhotoUploadForm()

    context = {'form': form}
    return render(request, 'dashboard/upload_photo.html', context)

@login_required
def edit_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if request.method == 'POST':
        form = PhotoEditForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()  # This will save all changes, including the category
            # Redirect after saving, possibly to the new category's album page
            return redirect('albums')
    else:
        form = PhotoEditForm(instance=photo)

    return render(request, 'dashboard/edit_photo.html', {'form': form, 'photo': photo})

@login_required
def albums(request):
    # Get categories with the photo count for the logged-in user
    categories = Category.objects.annotate(
        photo_count=Count('photo', filter=models.Q(photo__user=request.user))
    )
    
    context = {
        'categories': categories,
    }
    return render(request, 'dashboard/albums.html', context)

@login_required
def album_photos(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    photos_list = Photo.objects.filter(category=category, user=request.user).order_by('-uploaded_at')
    
    # Pagination
    paginator = Paginator(photos_list, 30)  # Show 10 photos per page
    page_number = request.GET.get('page')
    
    try:
        photos = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        photos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        photos = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/album_photos.html', {'category': category, 'photos': photos})


@csrf_exempt
def upload_image_tinymce(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']
        image_path = os.path.join("uploads", image.name)
        image_name = default_storage.save(image_path, ContentFile(image.read()))
        image_url = request.build_absolute_uri(settings.MEDIA_URL + image_name)

        return JsonResponse({'location': image_url})  # ✅ TinyMCE needs "location"

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    photo.delete()
    return redirect(request.META.get('HTTP_REFERER', 'albums'))


@login_required
def photo_sales(request):
    # Get the logged-in photographer's user ID
    photographer_id = request.user.id

    # Get the commission percentage for the logged-in photographer
    commission = BopCommission.objects.get()
    #commission_percentage = photographer_profile.commission_percentage / 100  # Convert to a fraction

    # Filter orders where the product's photographer is the logged-in user
    orders = Orders.objects.filter(items__photo_owner__user=photographer_id).distinct().prefetch_related('items')

    # Calculate commission and final amounts
    for order in orders:
        order.commission_percentage = commission.commission_percentage 
        order.final_amount = order.total_amount - order.total_amount * commission.commission_percentage / 100

    # Add pagination (10 orders per page)
    paginator = Paginator(orders, 50)  # Show 10 orders per page

    # Get the current page number from the request
    page_number = request.GET.get('page')

    # Get the orders for the requested page
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,  # Use 'orders' for pagination in the template
        'commission_percentage': commission.commission_percentage  * 100,
    }
    return render(request, 'dashboard/sales.html', context)

