from django.urls import path
from .views import StoryView, StoryList, LanguageView, StorySentencesView, \
    StoryRequestView, WordInsertionView, WordInsertionByStoryView

urlpatterns = [
    path('create-story/', StoryView.as_view(), name='create_story'),
    path('stories/', StoryList.as_view(), name='stories'),
    path('stories/<int:id>/', StorySentencesView.as_view(), name='sentences'),
    path('languages/', LanguageView.as_view(), name='stories'),
    path('test-word-insertion/', WordInsertionView.as_view(),
         name='word_insertion'),
    path('test-word-insertion-by-story/<int:id>/',
         WordInsertionByStoryView.as_view(), name='word_insertion_by_story'),
    path('stories/story-params/', StoryRequestView.as_view(), name='stories'),
]
