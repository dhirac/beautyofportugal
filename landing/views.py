from pyexpat.errors import messages
from time import timezone
from django.shortcuts import redirect, render
from cms.models import Blog, Post, Category, Photo, Event
from django.shortcuts import (get_object_or_404,
                              render, 
                              HttpResponseRedirect)
from cms.forms import EventRegistrationForm

from django.http import JsonResponse


from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import requests


# Create your views here.
def landing(request):
     
    categories = Category.objects.all()

    event = Event.objects.order_by('-id').first()


    context = {
        "categories" : categories,
        "event": event
    }

    return render(request,'landing.html',context)


def gallery(request, category_slug):
    # Get the category object based on the slug
    category = get_object_or_404(Category, slug=category_slug)

    # Get search query and price filters from the request
    query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)

    # Filter photos by category
    photos = Photo.objects.filter(category=category)

    # Apply search filter if a query is provided
    if query:
        photos = photos.filter(title__icontains=query) | photos.filter(description__icontains=query)

    # Apply price filter if min_price or max_price is provided
    if min_price:
        photos = photos.filter(price__gte=min_price)
    if max_price:
        photos = photos.filter(price__lte=max_price)

    # Debug print to verify filtered photos
    print(photos, "Filtered Photos")

    # Pass the filtered photos and category to the context
    context = {
        "categories": category,
        "photos": photos
    }

    # Render the gallery template with the context
    return render(request, 'gallery.html', context)

# Create your views here.
def registration(request):
     
    return render(request,'registration.html')



def photo_detail(request, slug):
    # Fetch the photo by slug (ensure it's using the Photo model)
    photo = get_object_or_404(Photo, slug=slug)

    # Increment the total views
    photo.total_views += 1
    photo.save()

    # Render the template with the photo details
    return render(request, 'photo_detail.html', {'photo': photo})



def photographers(request):
   
    return render(request, 'photographers.html')



def about_us(request):
   
    return render(request, 'aboutus.html')


def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, "blog.html", {"blogs": blogs})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    latest_blogs = Blog.objects.exclude(id=blog.id).order_by('-created_at')[:5]
    return render(request, "blog_detail.html", {
        "blog": blog,
        "latest_blogs": latest_blogs
    })



def event_detail(request, id):
    event = get_object_or_404(Event, id=id)

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.save()
            return JsonResponse({'success': True, 'message': "Successfully registered!"})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    else:
        form = EventRegistrationForm()

    return render(request, "event_detail.html", {"event": event, "form": form})


def contact(request):
    if request.method == "POST":
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        error = []

        # --- reCAPTCHA validation ---
        recaptcha_response = request.POST.get('g-recaptcha-response')
        recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
        recaptcha_data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        recaptcha_result = requests.post(recaptcha_url, data=recaptcha_data).json()

        if not recaptcha_result.get('success'):
            error.append("Invalid reCAPTCHA. Please try again.")

        if error:
            return render(request, "contact.html", {
                'error': error,
                'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY  # <-- use public key, not secret
            })

        # --- Send email via Brevo API ---
        full_message = f"""
        You have a new contact form submission from your website Beauty Of Portugal:

        From: {fname} {lname}
        Email: {email}
        
        Subject: {subject}
        
        Message:
        {message}
        """

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,   # define in settings.py
            "content-type": "application/json",
        }
        payload = {
            "sender": {"name": "Beauty Of Portugal", "email": "no-reply@beautyofportugal.com"},
            "to": [{"email": "pjdhirajshrestha@gmail.com"}],
            "subject": f"Contact Form: {subject}",
            "htmlContent": f"<pre>{full_message}</pre>"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            messages.success(request, "Your message has been sent successfully! We will get back to you soon.")
        except requests.exceptions.RequestException as e:
            print(f"❌ Brevo error: {e}")
            messages.error(request, "There was a problem sending your message. Please try again later.")

        return redirect("contact")

    # GET request, render form
    return render(request, "contact.html", {
        'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY
    })