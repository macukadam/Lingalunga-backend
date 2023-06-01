import re
import json
import traceback

from adrf import views as adrf_views
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework import permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from social_django.utils import load_strategy
from social_core.exceptions import AuthException
from social_core.backends.google import GoogleOAuth2
from lingalunga_server.apps.accounts.utils import generate_email_verification_token, authenticate
from lingalunga_server.apps.accounts.utils import send_verification_email, \
    google_get_or_create_user, send_reset_password_email
from lingalunga_server.apps.accounts.models import User
from lingalunga_server.apps.accounts.serializers import UserRegistrationSerializer
from lingalunga_server.apps.openai.models import SavedWord, CompletedStory


class CompletedStoryView(adrf_views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request):
        data = json.loads(request.body)
        user = request.user

        story_id = data.get('story')

        try:
            await CompletedStory.objects.aget(id=story_id, user=user)
        except CompletedStory.DoesNotExist:
            await CompletedStory(
                user=user,
                story_id=story_id
            ).asave()

        return JsonResponse({"status": "OK"}, status=201)

    async def get(self, request):
        user = request.user
        id = request.GET.get('id')

        if id:
            completed_stories = [s async for s in CompletedStory.objects
                                 .filter(user=user, id=id).values()]
        else:
            completed_stories = [s async for s in CompletedStory.objects
                                 .filter(user=user).values()]

        return JsonResponse({"completed_stories":
                             completed_stories}, status=200)


class SavedWordView(adrf_views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request):
        data = json.loads(request.body)
        user = request.user

        word_id = data.get('word')
        sentence_id = data.get('sentence')
        translation_sentence_id = data.get('translation_sentence')
        story_id = data.get('story')

        try:
            await SavedWord.objects.aget(sentence_id=sentence_id,
                                         word_id=word_id,
                                         story_id=story_id,
                                         user=user)
        except SavedWord.DoesNotExist:
            await SavedWord(
                user=user,
                word_id=word_id,
                sentence_id=sentence_id,
                translation_sentence_id=translation_sentence_id,
                story_id=story_id,
                translation=data.get('translation'),
            ).asave()

        return JsonResponse({'status': 'OK'}, status=201)

    async def delete(self, request):
        id = request.GET.get('id', None)
        user = request.user

        word = await SavedWord.objects.aget(id=id, user=user)
        await word.adelete()
        return JsonResponse({'status': 'OK', 'detail': 'Deleted'}, status=201)

    async def get(self, request):
        id = request.GET.get('id', None)
        user = request.user

        if id:
            saved_words = [s async for s in SavedWord.objects
                           .filter(user=user, id=id)
                           .values('id', 'word__text', 'translation',
                                   'sentence__id', 'sentence__text',
                                   'translation_sentence__id',
                                   'translation_sentence__text', 'story__id')]
        else:
            saved_words = [s async for s in SavedWord.objects
                           .filter(user=user)
                           .values('id', 'word__text', 'translation',
                                   'sentence__id', 'sentence__text',
                                   'translation_sentence__id',
                                   'translation_sentence__text', 'story__id')]

        return JsonResponse({"saved_words": saved_words}, status=200)


class VerifyEmailView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, _, uidb64, token):
        user = None
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponse(b'Activation link is invalid!')

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponse(b'Email verification successful.')
        else:
            return HttpResponse(b'Email verification failed.')


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


def password_reset_success(request):
    return render(request, 'reset_password_success.html')


class ForgetPasswordView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64=None, token=None):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        return render(request, 'reset_password.html', context)

    def post(self, request):
        email = request.data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                send_reset_password_email(request, user, uid, token)

                return Response({'status': 'OK'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                pass
        return Response({'error': 'Invalid Email'},
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid link'},
                            status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            new_password = request.data.get('password')
            if new_password:
                # check password validity
                if len(new_password) < 8:
                    return Response({'error': 'Password too short. It should be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)
                elif not re.search('[A-Za-z]', new_password):
                    return Response({'error': 'Password should have at least one letter.'}, status=status.HTTP_400_BAD_REQUEST)
                elif not re.search('[0-9]', new_password):
                    return Response({'error': 'Password should have at least one number.'}, status=status.HTTP_400_BAD_REQUEST)
                elif not re.search('[^A-Za-z0-9]', new_password):
                    return Response({'error': 'Password should have at least one special character.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user.set_password(new_password)
                    user.save()
                    return Response({'status': 'Password reset successful.'},
                                    status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Password not provided'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid link'},
                            status=status.HTTP_400_BAD_REQUEST)


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
            'username': user.username,
            'email': user.email,
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
                'username': user.username,
                'email': user.email,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception:
            traceback.print_exc()
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class UpdateAppData(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request):
        user = request.user
        user.app_data = request.data
        user.asave()
        return Response(status=status.HTTP_200_OK)
