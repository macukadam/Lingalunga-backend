from django.urls import path
from .views import GetAllFiles, GetObjectUrls

urlpatterns = [
    path('all-files/', GetAllFiles.as_view()),
    path('get-object-urls/', GetObjectUrls.as_view()),
]
