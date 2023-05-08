from django.urls import path
from .views import StoryView, StoryList, LanguageView, StorySentencesView, \
    StoryRequestView, WordInsertionView

urlpatterns = [
    path('create-story/', StoryView.as_view(), name='create_story'),
    path('stories/', StoryList.as_view(), name='stories'),
    path('stories/<int:id>/', StorySentencesView.as_view(), name='sentences'),
    path('languages/', LanguageView.as_view(), name='stories'),
    path('test-word-insertion/', WordInsertionView.as_view(), name='test_word_insertion'),
    path('stories/story-params/', StoryRequestView.as_view(), name='stories'),
]
