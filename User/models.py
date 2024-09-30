from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # Create the user instance
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Set the password with hashing
        user.generate_verification_code()  # Generate verification code upon registration
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Ensure superuser has is_staff and is_superuser set to True
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):  # Inherit from PermissionsMixin
    email = models.EmailField(unique=True)
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)

    # Personal Information
    role = models.CharField(max_length=10, choices=[('patient', 'Patient'), ('caretaker', 'Caretaker')], blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    bloodGroup = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True, null=True)
    disease = models.CharField(max_length=100, blank=True, null=True)
    diseaseStartDate = models.DateField(blank=True, null=True)
    profileComplete = models.BooleanField(default=False)

    phoneVerified = models.BooleanField(default=False)
    verificationCode = models.CharField(max_length=6, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  # Add this field for superuser support

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def generate_verification_code(self):
        """Generate a random 6-digit verification code."""
        self.verificationCode = str(random.randint(100000, 999999))
        self.save()

    def verify_code(self, code):
        """Verify the provided code against the stored verification code."""
        if self.verificationCode == code:
            self.phoneVerified = True
            self.verificationCode = None  # Clear verification code after successful verification
            self.save()
            return True
        return False