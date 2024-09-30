# urls.py (in your app directory)
from django.urls import path
from .views import (
    PhoneAuthView,
    EmailLoginView,
    CompleteProfileView,
    UserRoleView,
    dashboard_view
)
from social_django.views import complete

urlpatterns = [
    path('phoneAuth/', PhoneAuthView.as_view(), name='phone_auth'),
    path('dashboard/', dashboard_view, name='admin-dashboard'),
    path('loginEmail/', EmailLoginView.as_view(), name='email-login'),
    path('completeProfile/', CompleteProfileView.as_view(), name='complete-profile'),
    path('userRole/', UserRoleView.as_view(), name='user-role'),
    path('authGoogle/', complete, name='google-login', kwargs={'backend': 'google-oauth2'}),
    path('authApple/', complete, name='apple-login', kwargs={'backend': 'apple-id'}),
]
