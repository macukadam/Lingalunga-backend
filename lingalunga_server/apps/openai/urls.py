from django.urls import path
from .views import StoryView, StoryList

urlpatterns = [
    path('create-story/', StoryView.as_view(), name='create_story'),
    path('stories/', StoryList.as_view(), name='stories'),
]
