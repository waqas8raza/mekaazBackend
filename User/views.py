from rest_framework import status
from django.shortcuts import render,redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from .models import User, Disease
from Subscription.models import SubscriptionPlan, UserSubscription
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count, Sum
from django.contrib import messages
from .serializers import (
    PhoneRegisterSerializer,
    EmailLoginSerializer,
    CompleteProfileSerializer,
    CaretakerProfileSerializer,
    UserRoleSerializer
)

def admin_login(request):
	if request.method == 'POST':
		if request.POST.get('email') is None or request.POST.get('password') is None:
			return render(request,'auth-login.html',context={'bad_request':'please provide correct email or password'})
		else:
			user = authenticate(email=request.POST.get('email'),password = request.POST.get('password'))
			if user:
				login(request,user)
				return redirect('admin-dashboard')
			else:
				return render(request,'auth-login.html',context={'credential_error':'Invalid credentials'})

	return render(request,'auth-login.html')

def dashboard_view(request):
    # Count of total users, patients, and caretakers
    total_users = User.objects.count()
    total_patients = User.objects.filter(role='patient').count()
    total_caretakers = User.objects.filter(role='caretaker').count()

    # Plan purchases and earnings
    subscriptions = UserSubscription.objects.values('plan__name').annotate(plan_count=Count('plan'))
    earnings = SubscriptionPlan.objects.aggregate(total_earnings=Sum('usersubscription__plan__price'))

    # Prepare data for chart rendering
    plan_names = [sub['plan__name'] for sub in subscriptions]
    plan_counts = [sub['plan_count'] for sub in subscriptions]

    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_caretakers': total_caretakers,
        'plan_names': plan_names,
        'plan_counts': plan_counts,
        'total_earnings': earnings['total_earnings'] if earnings['total_earnings'] else 0,
    }
    return render(request, 'dashboard.html', context)

def dashboardUser_view(request):
    # Fetch users with role "patient"
    patients = User.objects.filter(role='patient')
    # Fetch users with role "caretaker"
    caretakers = User.objects.filter(role='caretaker')

    # Count total patients and caretakers
    total_patients = patients.count()
    total_caretakers = caretakers.count()

    return render(request, 'user.html', {
        'patients': patients,
        'caretakers': caretakers,
        'total_patients': total_patients,
        'total_caretakers': total_caretakers
    })

def dashboardSubscription_view(request):
    plans = SubscriptionPlan.objects.all()
    user_subscriptions = UserSubscription.objects.all()

    return render(request, 'subscription.html', context={
        'user': request.user,
        'plans': plans,
        'user_subscriptions': user_subscriptions
    })

def edit_plan_view(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if request.method == 'POST':
        plan.name = request.POST.get('name')
        plan.price = request.POST.get('price')
        plan.description = request.POST.get('description')
        plan.save()

        messages.success(request, 'Subscription plan updated successfully.')
        return redirect('admin-subscription')

    return render(request, 'subscription.html', {'plan': plan})

def delete_plan_view(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Subscription plan deleted successfully.')
        return redirect('admin-subscription')

    return render(request, 'subscription.html', {'plan': plan})

def logout_view(request):
    logout(request)
    return redirect('admin-login')

class PhoneAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phoneNumber = request.data.get('phoneNumber')
        verificationCode = request.data.get('verificationCode')

        if not phoneNumber:
            return Response({'error': 'Phone number is required.', 'statusCode': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phoneNumber=phoneNumber)

            if verificationCode:
                if user.verify_code(verificationCode):
                    user.phoneVerified = True
                    user.save()

                    token, created = Token.objects.get_or_create(user=user)

                    return Response({
                        'message': 'Phone number verified successfully!',
                        'user': {
                            'phoneNumber': user.phoneNumber,
                            'verificationCode': user.verificationCode,
                            'phoneVerified': user.phoneVerified,
                            'profileComplete': user.profileComplete,

                        },'statusCode': status.HTTP_200_OK,
                        'token': token.key,
                    }, status=status.HTTP_200_OK)

                return Response({'error': 'Invalid verification code.', 'statusCode': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            # Generate and send verification code
            user.generate_verification_code()
            # TODO: Send SMS with the verification code
            print(f"New verification code for {user.phoneNumber}: {user.verificationCode}")
            user.save()

            return Response({
                'message': 'Verification code sent successfully.',
                'user': {
                    'phoneNumber': user.phoneNumber,
                    'verificationCode': user.verificationCode,
                    'phoneVerified': user.phoneVerified,
                    'profileComplete': user.profileComplete,
                },'statusCode': status.HTTP_200_OK,
                'token': 'No Token',
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Create a new user if not found
            user = User(phoneNumber=phoneNumber)

            # OPTIONAL: Set a default email if needed, or remove email requirement from the model
            # user.email = "default@example.com"  # Uncomment if you need a default email

            user.generate_verification_code()
            # TODO: Send SMS with the verification code
            print(f"Verification code for {user.phoneNumber}: {user.verificationCode}")

            try:
                user.save()  # Attempt to save the new user
            except IntegrityError:
                return Response({'error': 'A user with this phone number already exists.', 'statusCode': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'message': 'User registered successfully! Verification code sent.',
                'user': {
                    'phoneNumber': user.phoneNumber,
                    'verificationCode': user.verificationCode,
                    'phoneVerified': user.phoneVerified,
                    'profileComplete': user.profileComplete,
                },'statusCode': status.HTTP_200_OK,
                'token': Token.key,
            }, status=status.HTTP_201_CREATED)



class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(request, email=email, password=password)

            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)

                return Response({
                    'message': 'Login successful!',
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'phoneVerified': user.phoneVerified,
                        'profileComplete': user.profileComplete
                    },
                    'statusCode': status.HTTP_200_OK
                }, status=status.HTTP_200_OK)

            else:
                user = User.objects.create_user(email=email, password=password)
                user.save()

                # Get or create token for the user
                token, _ = Token.objects.get_or_create(user=user)

                return Response({
                    'message': 'User created successfully!',
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'phoneVerified': user.phoneVerified,
                        'profileComplete': user.profileComplete
                    },
                    'statusCode': status.HTTP_200_OK
                }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteProfileView(APIView):
    def get(self, request):
        user = request.user  # Get the current authenticated user
        user_data = {
            'name': user.name,
            'bloodGroup': user.bloodGroup,
            'dob': user.dob,
            'gender': user.gender,
            'address': user.address,
            'diseases': [
                {'name': disease.name, 'start_date': disease.start_date}
                for disease in user.diseases.all()
            ],
            'profileComplete': user.profileComplete
        }
        return Response(user_data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = CompleteProfileSerializer(data=request.data)
        if serializer.is_valid():
            user.name = serializer.validated_data.get('name', user.name)
            user.bloodGroup = serializer.validated_data.get('bloodGroup', user.bloodGroup)
            user.dob = serializer.validated_data.get('dob', user.dob)
            user.gender = serializer.validated_data.get('gender', user.gender)
            user.address = serializer.validated_data.get('address', user.address)

            # Handle multiple diseases
            diseases_data = serializer.validated_data.get('diseases', [])
            user.diseases.all().delete()  # Optional: Clear existing diseases
            for disease_data in diseases_data:
                Disease.objects.create(user=user, **disease_data)  # Create new disease entries

            user.profileComplete = True
            user.save()

            return Response({
                'message': 'Profile updated successfully!',
                'user': {
                    'name': user.name,
                    'bloodGroup': user.bloodGroup,
                    'dob': user.dob,
                    'gender': user.gender,
                    'address': user.address,
                    'diseases': [
                        {'name': disease.name, 'start_date': disease.start_date}
                        for disease in user.diseases.all()
                    ],
                    'profileComplete': user.profileComplete
                },
                'statusCode': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        serializer = CompleteProfileSerializer(data=request.data)

        if serializer.is_valid():
            user.name = serializer.validated_data['name']
            user.bloodGroup = serializer.validated_data['bloodGroup']
            user.dob = serializer.validated_data['dob']
            user.gender = serializer.validated_data['gender']
            user.address = serializer.validated_data['address']

            # Handle multiple diseases
            diseases_data = serializer.validated_data.get('diseases', [])
            user.diseases.all().delete()  # Clear existing diseases
            for disease_data in diseases_data:
                Disease.objects.create(user=user, **disease_data)

            user.profileComplete = True  # Mark the profile as complete
            user.save()

            return Response({
                'message': 'Profile updated successfully!',
                'user': {
                    'name': user.name,
                    'bloodGroup': user.bloodGroup,
                    'dob': user.dob,
                    'gender': user.gender,
                    'address': user.address,
                    'diseases': [
                        {'name': disease.name, 'start_date': disease.start_date}
                        for disease in user.diseases.all()
                    ],
                    'profileComplete': user.profileComplete
                },
                'statusCode': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({
            'message': 'Profile deleted successfully!',
            'statusCode': status.HTTP_204_NO_CONTENT
        }, status=status.HTTP_204_NO_CONTENT)

class CaretakerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Ensure the user is a caretaker
        if user.role != 'caretaker':
            return Response({
                "error": "You do not have permission to view this profile.",
                "status_code": status.HTTP_403_FORBIDDEN
            }, status=status.HTTP_403_FORBIDDEN)

        user_data = {
            'name': user.name,
            'relationWithPatient': user.relationWithPatient,
            'dob': user.dob,
            'gender': user.gender,
            'profileComplete': user.profileComplete
        }
        return Response(user_data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        # Ensure the user is a caretaker
        if user.role != 'caretaker':
            return Response({
                "error": "You do not have permission to update this profile.",
                "status_code": status.HTTP_403_FORBIDDEN
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = CaretakerProfileSerializer(data=request.data)

        if serializer.is_valid():
            user.name = serializer.validated_data['name']
            user.relationWithPatient = serializer.validated_data['relationWithPatient']
            user.dob = serializer.validated_data['dob']
            user.gender = serializer.validated_data['gender']
            user.profileComplete = True  # Mark the profile as complete
            user.save()

            return Response({
                'message': 'Profile updated successfully!',
                'user': {
                    'name': user.name,
                    'relationWithPatient': user.relationWithPatient,
                    'dob': user.dob,
                    'gender': user.gender,
                    'profileComplete': user.profileComplete
                },
                'statusCode': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Invalid data.",
            "details": serializer.errors,
            "status_code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user

        # Ensure the user is a caretaker
        if user.role != 'caretaker':
            return Response({
                "error": "You do not have permission to update this profile.",
                "status_code": status.HTTP_403_FORBIDDEN
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = CaretakerProfileSerializer(data=request.data)

        if serializer.is_valid():
            user.name = serializer.validated_data['name']
            user.relationWithPatient = serializer.validated_data['relationWithPatient']
            user.dob = serializer.validated_data['dob']
            user.gender = serializer.validated_data['gender']
            user.profileComplete = True  # Mark the profile as complete
            user.save()

            return Response({
                'message': 'Profile updated successfully!',
                'user': {
                    'name': user.name,
                    'relationWithPatient': user.relationWithPatient,
                    'dob': user.dob,
                    'gender': user.gender,
                    'profileComplete': user.profileComplete
                },
                'statusCode': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Invalid data.",
            "details": serializer.errors,
            "status_code": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

class UserRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the current authenticated user
        return Response({
            'role': user.role,
            'statusCode': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user  # Get the current authenticated user
        serializer = UserRoleSerializer(data=request.data)

        if serializer.is_valid():
            user.role = serializer.validated_data['role']
            user.save()
            return Response({
                'message': 'Role updated successfully!',
                'role': user.role,
                'statusCode': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
