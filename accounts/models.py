from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    success = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{status} login for {self.username} from {self.ip_address} at {self.timestamp}"

class CustomUserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('customer', 'customer'),
        ('photographer', 'photographer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES)
    
    def __str__(self):
        return self.user.username




class BopCommission(models.Model):
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    def __str__(self):
        return f"{self.commission_percentage}"
