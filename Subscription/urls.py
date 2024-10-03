from django.urls import path
from .views import SubscriptionPlanListView, UserSubscriptionListView, PurchaseSubscriptionView, AddCaretakerView

urlpatterns = [
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('subscriptions/', UserSubscriptionListView.as_view(), name='user-subscriptions'),
    path('purchase/', PurchaseSubscriptionView.as_view(), name='purchase-subscription'),
    path('caretakers/', AddCaretakerView.as_view(), name='add-caretaker'),
]
