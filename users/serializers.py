from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from users.tokens import account_activation_token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'phone', 'address']
        extra_kwargs = {
            'username': {'required': False}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data.get('username'),
            phone=validated_data.get('phone'),
            address=validated_data.get('address'),
            is_active=False
        )

        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"http://localhost:8000/api/users/activate/{uid}/{token}/"

        subject = "Активация аккаунта"
        message = render_to_string('activation_email.html', {
            'user': user,
            'activation_link': activation_link,
        })
        send_mail(subject, message, None, [user.email], html_message=message)

        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        password = attrs.get('password')

        if not (email or username):
            raise ValidationError({'error': 'Требуется email или username'})
        
        if not password:
            raise ValidationError({'error': 'Пароль обязателен'})

        user = authenticate(
            request=self.context.get('request'),
            username=email or username,
            password=password
        )

        if not user:
            raise ValidationError({'error': 'Неверные учетные данные'})
        
        if not user.is_active:
            raise ValidationError({'error': 'Аккаунт не активирован. Проверьте вашу почту.'})

        attrs['user'] = user
        return attrs