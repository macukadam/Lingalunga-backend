from django.urls import path
from .views import GetAllFiles, GetObjectUrls, call_dummy_task

urlpatterns = [
    path('all-files/', GetAllFiles.as_view()),
    path('get-object-urls/', GetObjectUrls.as_view()),
    path('call-dummy-task/', call_dummy_task, name='call_dummy_task'),
]
