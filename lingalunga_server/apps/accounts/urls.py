from social_django.views import complete
from django.urls import path
from .views import RegisterView, LoginView, RefreshTokenView, \
    SocialLoginView, UpdateAppData, SavedWordView, CompletedStoryView, \
    ForgetPasswordView, password_reset_success

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('google/', SocialLoginView.as_view(), name='google_login'),
    path('google/callback/', complete,
         {'backend': 'google-oauth2'}, name='google-oauth2-callback'),
    path('update-app-data/', UpdateAppData.as_view(), name='update_app_data'),
    path('save-word/', SavedWordView.as_view(), name='saved_words'),
    path('completed-stories/', CompletedStoryView.as_view(),
         name='completed_stories'),
    path('password-reset/', ForgetPasswordView.as_view(),
         name='password_reset'),
    path('password-reset-success/', password_reset_success,
         name='password_reset_success'),
    path('password-reset/<uidb64>/<token>/', ForgetPasswordView.as_view(),
         name='password_reset_confirm'),]
