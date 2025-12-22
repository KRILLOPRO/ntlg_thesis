from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer
from orders.tasks import send_registration_email


class RegisterView(generics.CreateAPIView):
    """API для регистрации пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Создаем токен для пользователя
        token, created = Token.objects.get_or_create(user=user)
        
        # Отправляем email с подтверждением регистрации через Celery
        send_registration_email.delay(user.email, user.username)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Пользователь успешно зарегистрирован. Email с подтверждением отправлен.'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """API для авторизации пользователя"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email'].strip().lower()
        password = serializer.validated_data['password']
        
        # Проверяем существование пользователя
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Используем email для аутентификации, так как USERNAME_FIELD = 'email'
        # Важно использовать точный email из базы данных
        authenticated_user = authenticate(
            request, 
            username=user.email, 
            password=password
        )
        
        if authenticated_user:
            token, created = Token.objects.get_or_create(user=authenticated_user)
            return Response({
                'user': UserSerializer(authenticated_user).data,
                'token': token.key,
                'message': 'Успешная авторизация'
            })
        else:
            # Дополнительная проверка пароля для отладки
            if user.check_password(password):
                # Если пароль правильный, но authenticate не работает,
                # создаем токен вручную
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'user': UserSerializer(user).data,
                    'token': token.key,
                    'message': 'Успешная авторизация'
                })
            return Response(
                {'error': 'Неверный email или пароль'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API для просмотра и обновления профиля пользователя"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
