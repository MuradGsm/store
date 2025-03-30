from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserRegisterSerializer, UserLoginSerializer
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from users.tokens import account_activation_token
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            referesh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(referesh),
                'access': str(referesh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Ошибка активации: {e}")
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            if user.is_active:
                return Response({'status': 'Аккаунт уже активирован'}, status=400)
                
            user.is_active = True
            user.save()
            logger.info(f"Аккаунт {user.email} успешно активирован")
            return Response({'status': 'Аккаунт активирован!'}, status=200)
            
        logger.warning(f"Неудачная попытка активации (uidb64: {uidb64})")
        return Response({'error': 'Неверная ссылка активации'}, status=400)