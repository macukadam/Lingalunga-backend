from django.urls import path
from .views import GetAllFiles, GetObjectUrls, Voices

urlpatterns = [
    path('all-files/', GetAllFiles.as_view()),
    path('get-object-urls/', GetObjectUrls.as_view()),
    path('update-aws-voices/', Voices.as_view()),
]
