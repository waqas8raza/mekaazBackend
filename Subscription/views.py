from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import SubscriptionPlan, UserSubscription, Caretaker
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer, PurchaseSubscriptionSerializer, CaretakerSerializer
from django.utils.timezone import now
from django.db import IntegrityError

# List available subscription plans
class SubscriptionPlanListView(APIView):
    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        if not plans.exists():
            return Response({
                "error": "No subscription plans available.",
                "status_code": status.HTTP_404_NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response({
            "success": "Subscription plans fetched successfully.",
            "data": serializer.data,
            "status_code": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)

# List the user's purchased subscriptions
class UserSubscriptionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_subscriptions = UserSubscription.objects.filter(user=request.user)
        if not user_subscriptions.exists():
            return Response({
                "error": "No active subscriptions found.",
                "status_code": status.HTTP_404_NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSubscriptionSerializer(user_subscriptions, many=True)
        return Response({
            "success": "User subscriptions fetched successfully.",
            "data": serializer.data,
            "status_code": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)

# Purchase a subscription plan
class PurchaseSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PurchaseSubscriptionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            subscription = serializer.save()
            return Response({
                "success": "Subscription purchased successfully.",
                "data": UserSubscriptionSerializer(subscription).data,
                "status_code": status.HTTP_201_CREATED
            }, status=status.HTTP_201_CREATED)
        return Response({
            "error": "Invalid data.",
            "details": serializer.errors,
            "status_code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

# Add caretaker for a patient
class AddCaretakerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check for an active subscription
        user_subscription = UserSubscription.objects.filter(user=user, expiry_date__gte=now()).first()

        if not user_subscription:
            return Response({
                "error": "No active subscription found.",
                "statusCode": status.HTTP_403_FORBIDDEN
            }, status=status.HTTP_403_FORBIDDEN)

        caretakers_count = Caretaker.objects.filter(user=user).count()

        # Enforce subscription plan limits
        if user_subscription.plan and user_subscription.plan.name == 'Basic' and caretakers_count >= 5:
            return Response({
                "error": "You have reached the limit of 5 caretakers for the Basic plan.",
                "statusCode": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CaretakerSerializer(data=request.data)

        if serializer.is_valid():
            try:
                caretaker = serializer.save()  # This also creates a User with the caretaker role
                return Response({
                    "success": "Caretaker added successfully.",
                    "data": CaretakerSerializer(caretaker).data,
                    "statusCode": status.HTTP_201_CREATED
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({
                    "error": "A caretaker with this email or identifier already exists.",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)

        # Include detailed error messages from the serializer
        return Response({
            "error": "Invalid data.",
            "details": serializer.errors,
            "statusCode": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)
