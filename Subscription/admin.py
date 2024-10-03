from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, Caretaker

# Register your models here.
admin.site.register(SubscriptionPlan),
admin.site.register(UserSubscription),
admin.site.register(Caretaker),