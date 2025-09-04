from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from lib.token_generator import account_activation_token
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
import logging
from django.core.mail import EmailMessage
from .models import CustomUserProfile
from django.conf import settings
import requests
from .models import LoginAttempt
from django.utils import timezone
from datetime import timedelta


def boplogin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = []
    ip = get_client_ip(request)

    # Check if IP is blocked
    block_duration = getattr(settings, 'BLOCK_DURATION', 15)
    max_attempts = getattr(settings, 'MAX_FAILED_ATTEMPTS', 5)
    block_time = timezone.now() - timedelta(minutes=block_duration)
    recent_failed_attempts = LoginAttempt.objects.filter(
        ip_address=ip, success=False, timestamp__gte=block_time
    ).count()

    if recent_failed_attempts >= max_attempts:
        error.append(f"Too many failed login attempts. Try again after {block_duration} minutes.")
        return render(request, "registration.html", {'error': error})

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        # Log the attempt
        if user is not None:
            login(request, user)
            LoginAttempt.objects.create(username=username, success=True, ip_address=ip)
            return redirect('dashboard')
        else:
            LoginAttempt.objects.create(username=username, success=False, ip_address=ip)
            error.append("Username or password is incorrect")

    return render(request, "registration.html", {'error': error})


def signup(request):
    error = []
    success = []

    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Verify reCAPTCHA
        recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
        recaptcha_data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        recaptcha_result = requests.post(recaptcha_url, data=recaptcha_data).json()

        if not recaptcha_result.get('success'):
            error.append("Invalid reCAPTCHA. Please try again.")
        elif password != cpassword:
            error.append("Password and Confirm Password did not match.")
        elif User.objects.filter(username=username).exists():
            error.append("Username already taken.")
        elif User.objects.filter(email=email).exists():
            error.append("Email already registered.")
        else:
            # Create inactive user
            user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
            CustomUserProfile.objects.create(user=user, user_type='photographer')

            # Send activation email (same as your current code)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('account/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            email_message = EmailMessage(mail_subject, message, 'noreply@beautyofportugal.com', [email])
            email_message.content_subtype = "html"
            email_message.send()

            success.append("User created successfully. Please check your email to activate.")

    return render(request, "registration.html", {'error': error, 'success': success, 'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY})



def signup_photographer(request):

    error=[]
    success=[]

    if request.method == "POST" :

        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        cpassword = request.POST['cpassword']


        if password == cpassword:
           
           user = User.objects.create_user(username,email,password,is_active=False)
           user.save()

           try:
                test = CustomUserProfile.objects.create(user=user, user_type='photographer')
                test.save()
                print(test, "CustomUserProfile created successfully")
           except Exception as e:
                print("Error while creating CustomUserProfile:", e)
           
          

           uid = urlsafe_base64_encode(force_bytes(user.pk))
           token = account_activation_token.make_token(user)


           # Sending the activation email
           current_site = get_current_site(request)
           mail_subject = 'Activate your account'
           message = render_to_string('account/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid ,
                'token': token,
             })

             

           to_email = email
           email = EmailMessage(mail_subject, message, 'cloudinovater@gmail.com', [to_email])

            # Set the content type to HTML
           email.content_subtype = "html"  
           email.send()


           success.append("User create successfully. Please activate your account by using the link send in your Email. ")

        else:
            error.append("Password and Confirm Password did not matched")
               
    return render(request, "registration_photographer.html",{'error': error,'success':success})

# Initialize logger
logger = logging.getLogger(__name__)

User = get_user_model()

def activate(request, uidb64, token):
    try:
        # Decode the user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        logger.info(f"User found: {user} with UID: {uid}")

    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.error(f"Error in user lookup: {e}")
        user = None

    # Validate the token and activate the user
    if user is not None:
        token_is_valid = account_activation_token.check_token(user, token)
        logger.info(f"Token validation status: {token_is_valid}")

        if token_is_valid:
            user.is_active = True
            user.save()
            print('done bro is triggered')
            print(f"User activated: {user}")
            return render(request, 'account/activation_complete.html')
        else:
            print("Invalid token used for activation.")
            return render(request, 'account/activation_invalid.html')

    else:
        logger.warning("No valid user found for activation.")
        return render(request, 'account/activation_invalid.html')




def boplogout(request):
    # Log out the user.
    # since function cannot be same as django method, esle it will turn into recursive calls
    logout(request)
    # Return to homepage.
    return redirect('register')


def get_client_ip(request):
    """Retrieve the client IP address from the request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip