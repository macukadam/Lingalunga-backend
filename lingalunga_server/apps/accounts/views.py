import traceback
from social_django.utils import load_strategy
from social_core.exceptions import AuthException
from social_core.backends.google import GoogleOAuth2
from rest_framework import status, permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from lingalunga_server.apps.accounts.serializers import UserRegistrationSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from lingalunga_server.apps.accounts.utils import send_verification_email,\
    google_get_or_create_user
from lingalunga_server.apps.accounts.models import User
from lingalunga_server.apps.accounts.utils import generate_email_verification_token, authenticate


class VerifyEmailView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        user = None
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponse('Activation link is invalid!')

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponse('Email verification successful.')
        else:
            return HttpResponse('Email verification failed.')


class RefreshTokenView(TokenRefreshView):
    pass


class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                if user.is_active:
                    return Response({'error': 'User already exists.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'User already exists but is not active.'})
            except User.DoesNotExist:
                user = serializer.save()
                user.set_password(serializer.validated_data['password'])
                user.is_active = False
                user.save()

            uid, token = generate_email_verification_token(user)
            send_verification_email(request, user, uid, token)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = authenticate(email=email, password=password)
        except User.DoesNotExist:
            traceback.print_exc()
            return Response({'error': 'User does not exsist!'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            traceback.print_exc()
            if e.__str__() == 'Incorrect credentials.':
                return Response({'error': 'Incorrect credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
            elif e.__str__() == 'User is not active.':
                return Response({'error': 'User is not active.'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        refresh = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(response_data, status=status.HTTP_200_OK)


class GoogleLoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')
        email = request.data.get('email')

        try:
            strategy = load_strategy(request)
            backend = GoogleOAuth2(strategy=strategy)
            user = google_get_or_create_user(
                backend, access_token, email=email)

            if user is None:
                raise AuthException(backend)

            if not user.is_active:
                user.is_active = True
                user.save()

            refresh = RefreshToken.for_user(user)
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception:
            traceback.print_exc()
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
