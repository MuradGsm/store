from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

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
            username=validated_data.get('username', ''),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
        )
        return user
    

class UserLoginSerializer(serializers.Serializer):
    # Делаем оба поля необязательными
    email = serializers.EmailField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        password = attrs.get('password')

        # Проверяем, что указан ХОТЯ БЫ ОДИН идентификатор
        if not (email or username):
            raise ValidationError('Требуется email или username')

        # Аутентифицируем пользователя
        user = authenticate(
            request=self.context.get('request'),
            username=email or username,  # Передаём то, что есть
            password=password
        )

        if not user:
            raise ValidationError('Неверные учетные данные')

        attrs['user'] = user
        return attrs