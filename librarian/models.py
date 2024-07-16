from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import pyotp
from django.conf import settings

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    available = models.BooleanField(default = True)
    issued = models.BooleanField(default=False)
    issued_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='issued_books')    
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
            
class UserProfile(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    otp_secret = models.CharField(max_length=16, default=pyotp.random_base32)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    is_librarian = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='user_profiles',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='user_profiles',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def generate_otp(self):
        totp = pyotp.TOTP(self.otp_secret, interval=300)
        return totp.now()

    def verify_otp(self, otp):
        totp = pyotp.TOTP(self.otp_secret, interval=300)
        return totp.verify(otp)