from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.utils import timezone

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    work_hours_per_day = models.IntegerField(default=8)
    preferred_working_time = models.CharField(
        max_length=20,
        choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')],
        default='morning'
        
    )
    max_tasks_per_day = models.IntegerField(default=5)
    break_interval_minutes = models.IntegerField(default=60)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class OTPVerification(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # OTP expires after 10 minutes
        expiry = self.created_at + timezone.timedelta(minutes=10)
        return not self.is_used and timezone.now() < expiry

    @staticmethod
    def generate_otp():
        return ''.join(random.choices(string.digits, k=6))

    def __str__(self):
        return f"{self.user.email} - {self.otp}"