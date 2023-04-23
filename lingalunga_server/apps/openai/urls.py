from django.urls import path
from .views import StoryView, StoryList, LanguageView, StorySentencesView

urlpatterns = [
    path('create-story/', StoryView.as_view(), name='create_story'),
    path('stories/', StoryList.as_view(), name='stories'),
    path('stories/<int:id>/', StorySentencesView.as_view(), name='sentences'),
    path('languages/', LanguageView.as_view(), name='stories'),
]
