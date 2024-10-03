from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, Caretaker
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

class CaretakerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    phoneNumber = serializers.CharField(max_length=15)

    class Meta:
        model = Caretaker
        fields = ['email', 'phoneNumber', 'gender', 'age', 'relationship', 'average_time']

    def create(self, validated_data):
        email = validated_data.get('email')
        phone_number = validated_data.get('phoneNumber')

        # Ensure a user instance is created or retrieved for the caretaker
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'phoneNumber': phone_number,
                'role': 'caretaker',
                'is_active': True
            }
        )

        # If user already exists, we update the phone number and role if necessary
        if not created:
            if not user.phoneNumber:
                user.phoneNumber = phone_number
            if user.role != 'caretaker':
                user.role = 'caretaker'
            user.save()

        # Now create the Caretaker instance
        caretaker = Caretaker.objects.create(
            user=user,
            email=email,
            phoneNumber=phone_number,
            gender=validated_data.get('gender'),
            age=validated_data.get('age'),
            relationship=validated_data.get('relationship'),
            average_time=validated_data.get('average_time')
        )
        return caretaker

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'description']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'plan', 'purchase_date', 'expiry_date']

class PurchaseSubscriptionSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()

    def validate_plan_id(self, value):
        try:
            SubscriptionPlan.objects.get(id=value)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid subscription plan ID.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        plan = SubscriptionPlan.objects.get(id=validated_data['plan_id'])

        # Set expiry date based on the plan (Free plan has a 7-day validity)
        if plan.name == 'Free':
            expiry_date = timezone.now() + timedelta(days=7)
        else:
            expiry_date = timezone.now() + timedelta(days=30)  # 30-day validity for paid plans

        # Create and save the user subscription
        user_subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            expiry_date=expiry_date
        )

        return user_subscription
