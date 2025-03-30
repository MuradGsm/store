from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators = [validate_password])

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'phone', 'address']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username'],
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', '')
        )
        return user
    

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not data.get('email') and not data.get('username'):
            raise serializers.ValidationError("Email or username is required.")
        return data