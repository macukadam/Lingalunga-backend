# from .tasks import generate_story
from lingalunga_server.apps.openai.tasks import generate_story
from rest_framework import permissions
from django.http import JsonResponse
from .models import Story, Sentence, Language
from lingalunga_server.apps.s3.tasks import synthesize_speech_and_upload_to_s3
from adrf import views
from rest_framework import generics
from .serializers import StorySerializer


class StoryList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Story.objects.all()
    serializer_class = StorySerializer


class StoryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request, *args, **kwargs):
        stories = await Story.objects.async_all()
        return JsonResponse(list(stories.values()), safe=False)

    async def post(self, request, *args, **kwargs):
        l1 = request.data.get('l1')
        l2 = request.data.get('l2')
        level = request.data.get('level')
        theme = request.data.get('theme')
        characters = request.data.get('characters')
        length = request.data.get('length')
        print(l1, l2, level, theme, characters, length)

        story_text = await generate_story(l1, l2, level, theme, characters, length)

        native_language = await Language.objects.aget(name='English')
        target_language = await Language.objects.aget(name='Spanish')

        story = Story(title='Dummy story', native_language=native_language,
                      target_language=target_language)
        await story.asave()

        for english_sentence, spanish_sentence in story_text:
            _, task_id = await synthesize_speech_and_upload_to_s3(english_sentence, voice_id='Joanna')
            native_sentence = Sentence(text=english_sentence,
                                       language=native_language, audio_key=task_id, story=story)
            await native_sentence.asave()

            _, task_id = await synthesize_speech_and_upload_to_s3(spanish_sentence, voice_id='Lucia')
            target_sentence = Sentence(text=spanish_sentence,
                                       language=target_language, audio_key=task_id, story=story)
            await target_sentence.asave()

        return JsonResponse({'status': 'success'})
