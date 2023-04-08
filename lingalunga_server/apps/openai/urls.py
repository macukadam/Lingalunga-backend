from django.urls import path
from .views import generate_dummy_story

urlpatterns = [
    path('generate-dummy-story/', generate_dummy_story, name='call_dummy_task'),
]
