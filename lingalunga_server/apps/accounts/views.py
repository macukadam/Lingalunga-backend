from social_django.utils import load_strategy
from social_core.exceptions import AuthException
from social_core.backends.google import GoogleOAuth2
from django.contrib.auth import authenticate
from rest_framework import status, permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from lingalunga_server.apps.accounts.serializers import UserRegistrationSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
import traceback


class RefreshTokenView(TokenRefreshView):
    pass


class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class GoogleLoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')

        try:
            strategy = load_strategy(request)
            backend = GoogleOAuth2(strategy=strategy)
            user = backend.do_auth(access_token)

            if user is None:
                raise AuthException(backend)

            refresh = RefreshToken.for_user(user)
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            print(response_data)

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception:
            traceback.print_exc()
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
