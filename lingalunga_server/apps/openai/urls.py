from django.urls import path
from .views import StoryView, StoryList, LanguageView, StorySentencesView, \
    StoryRequestView, WordView, TestWordInsertion

urlpatterns = [
    path('create-story/', StoryView.as_view(), name='create_story'),
    path('stories/', StoryList.as_view(), name='stories'),
    path('stories/<int:id>/', StorySentencesView.as_view(), name='sentences'),
    path('languages/', LanguageView.as_view(), name='stories'),
    path('get-words/<int:id>/', WordView.as_view(), name='get_words'),
    path('stories/story-params/', StoryRequestView.as_view(), name='stories'),
    path('stories/test-word-insertion/<int:id>', TestWordInsertion.as_view(),
         name='test_word_insertion'),
]
