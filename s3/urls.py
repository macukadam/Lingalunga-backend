from django.urls import path
from .views import GetAllFiles, GetObjectUrl

urlpatterns = [
    path('all-files/', GetAllFiles.as_view()),
    path('get-object-url/', GetObjectUrl.as_view()),
]
