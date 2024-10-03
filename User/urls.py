# urls.py (in your app directory)
from django.urls import path
from .views import (
    PhoneAuthView,
    EmailLoginView,
    CompleteProfileView,
    UserRoleView,
    dashboard_view,
    dashboardUser_view,
    dashboardSubscription_view,
    edit_plan_view,
    delete_plan_view,
    CaretakerProfileView,
    logout_view
)
from social_django.views import complete

urlpatterns = [
    path('phoneAuth/', PhoneAuthView.as_view(), name='phone_auth'),
    path('dashboard/', dashboard_view, name='admin-dashboard'),
    path('dashboardUser/', dashboardUser_view, name='admin-user'),
    path('dashboardSubscription/', dashboardSubscription_view, name='admin-subscription'),
    path('edit-plan/<int:plan_id>/', edit_plan_view, name='edit_plan'),
    path('delete-plan/<int:plan_id>/', delete_plan_view, name='delete_plan'),
    path('adminlogout/', logout_view, name='admin-logout'),
    path('loginEmail/', EmailLoginView.as_view(), name='email-login'),
    path('completeProfile/', CompleteProfileView.as_view(), name='complete-profile'),
    path('careTakercompleteProfile/', CaretakerProfileView.as_view(), name='careTakercomplete-profile'),
    path('userRole/', UserRoleView.as_view(), name='user-role'),
    path('authGoogle/', complete, name='google-login', kwargs={'backend': 'google-oauth2'}),
    path('authApple/', complete, name='apple-login', kwargs={'backend': 'apple-id'}),
]
