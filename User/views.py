from rest_framework import status
from django.shortcuts import render,redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import (
    PhoneRegisterSerializer,
    EmailLoginSerializer,
    CompleteProfileSerializer,
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
    return render(request, 'dashboard.html', context={'user': request.user})

class PhoneAuthView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        phoneNumber = request.data.get('phoneNumber')
        verificationCode = request.data.get('verificationCode')

        if not phoneNumber:
            return Response({'error': 'Phone number is required.' ,'statusCode': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

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
                            'phoneVerified': user.phoneVerified,
                            'profileComplete': user.profileComplete,
                            'token': token.key,
                            'statusCode': status.HTTP_200_OK
                        }
                    }, status=status.HTTP_200_OK)

                return Response({'error': 'Invalid verification code.','statusCode': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            user.generate_verification_code() 
            # TODO: Send SMS with the verification code
            print(f"New verification code for {user.phoneNumber}: {user.verificationCode}")
            user.save()

            return Response({
                'message': 'Verification code sent successfully.',
                'user': {
                    'phoneNumber': user.phoneNumber,
                },
                'statusCode': status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            user = User(phoneNumber=phoneNumber)
            user.generate_verification_code()
            # TODO: Send SMS with the verification code
            print(f"Verification code for {user.phoneNumber}: {user.verificationCode}")
            user.save()

            return Response({
                'message': 'User registered successfully! Verification code sent.',
                'user': {
                    'phoneNumber': user.phoneNumber,
                },
                'statusCode': status.HTTP_200_OK
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
                        'phoneVerified': user.phone_verified,
                        'profileComplete': user.profile_complete
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
            'disease': user.disease,
            'diseaseStartDate': user.diseaseStartDate,
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
            user.disease = serializer.validated_data.get('disease', user.disease)
            user.diseaseStartDate = serializer.validated_data.get('diseaseStartDate', user.diseaseStartDate)
            user.profileComplete = True
            user.save()
            return Response({
                'message': 'Profile updated successfully!',
                'user': {
                    'name': user.name,
                    'bloodGroup': user.bloodGroup,
                    'dob': user.dob,
                    'gender': user.gender,
                    'disease': user.disease,
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
    
class UserRoleView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view

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
