# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phoneNumber', 'role', 'bloodGroup', 'dob', 'gender', 'disease', 'diseaseStartDate', 'profileComplete')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'phoneVerified', 'verificationCode')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser')}),
    )
    list_display = ('email', 'name', 'is_staff', 'is_active', 'phoneVerified')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'phoneVerified')
    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ()
    radio_fields = {}
    actions = None

admin.site.register(User, UserAdmin)