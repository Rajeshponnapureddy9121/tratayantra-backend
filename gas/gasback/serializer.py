from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from .models import *
from django.contrib.auth import authenticate

class GasSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasSensor
        fields = '__all__'
        read_only_fields = ['user']

class GasReadingSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='sensor.sensor_name', read_only=True)
    location = serializers.CharField(source='sensor.location', read_only=True)
    
    class Meta:
        model = GasReading
        fields = '__all__'

class GasAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasAlert
        fields = '__all__'
        read_only_fields = ['user']

class PipelineSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineSection
        fields = '__all__'
        read_only_fields = ['user']

class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSchedule
        fields = '__all__'
        read_only_fields = ['user']

class GasRegulatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasRegulator
        fields = '__all__'
        read_only_fields = ['user']

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = '__all__'
        read_only_fields = ['user']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_image', 'notification_preferences']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    device_unique_code = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'device_unique_code', 'phone_number']

    def validate_phone_number(self, value):
        if UserProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        device_unique_code = validated_data.pop('device_unique_code')
        phone_number = validated_data.pop('phone_number')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user, device_unique_code=device_unique_code, phone_number=phone_number)
        return user

from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')
        if phone_number and password:
            profile = UserProfile.objects.filter(phone_number=phone_number).first()
            if not profile:
                raise serializers.ValidationError("Invalid mobile number or password.")
            user = authenticate(username=profile.user.username, password=password)
            if user and user.is_active:
                return user
            else:
                raise serializers.ValidationError("Invalid mobile number or password.")
        raise serializers.ValidationError("Both mobile number and password are required.")


