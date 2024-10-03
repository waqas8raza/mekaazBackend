from rest_framework import serializers
from .models import User, Disease

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

class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ['name', 'start_date']

class CompleteProfileSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    bloodGroup = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=True)
    address = serializers.CharField(required=True)
    diseases = DiseaseSerializer(many=True, required=True)

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
        extra_kwargs = {
            'role': {'required': True}
        }

class CaretakerProfileSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    relationWithPatient = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=True)