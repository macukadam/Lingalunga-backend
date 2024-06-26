"""lingalunga_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import WelcomeView, Privacy
from oauth2_provider.views import AuthorizationView
from lingalunga_server.apps.accounts.views import VerifyEmailView

urlpatterns = [
    path('', WelcomeView.as_view()),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('lingalunga_server.apps.accounts.urls')),
    path('api/s3/', include('lingalunga_server.apps.s3.urls')),
    path('api/openai/', include('lingalunga_server.apps.openai.urls')),
    path('authorize/', AuthorizationView.as_view(), name='authorize'),
    path('privacy/', Privacy.as_view(), name='privacy'),
    path('verify-email/<str:uidb64>/<str:token>/',
         VerifyEmailView.as_view(), name='verify-email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
