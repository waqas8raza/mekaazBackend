from rest_framework import serializers
from .models import User

class PhoneRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phoneNumber']

class VerifyPhoneSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    verification_code = serializers.CharField()

class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class CompleteProfileSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    bloodGroup = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=True)
    disease = serializers.CharField(required=True)
    diseaseStartDate = serializers.DateField(required=True)

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
        extra_kwargs = {
            'role': {'required': True}
        }