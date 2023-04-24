from django.urls import path
from .views import GetObjectUrls, Voices

urlpatterns = [
    path('get-object-urls/', GetObjectUrls.as_view()),
    path('update-aws-voices/', Voices.as_view()),
]
