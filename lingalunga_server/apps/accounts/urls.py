from django.urls import path
from .views import RegisterView, LoginView, RefreshTokenView, GoogleLoginView
from social_django.views import complete

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', complete,
         {'backend': 'google-oauth2'}, name='google-oauth2-callback'),
]
