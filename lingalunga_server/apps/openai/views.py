from lingalunga_server.apps.openai.tasks import generate_story
from rest_framework import permissions
from django.http import JsonResponse
from .models import Story, Sentence, Language
from lingalunga_server.apps.s3.models import Voice
from lingalunga_server.apps.s3.tasks import synthesize_speech_and_upload_to_s3, upload_image_to_s3
from adrf import views
from rest_framework import generics
from .serializers import StorySerializer


class LanguageView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request):
        languages = [lang async for lang in Language.objects.all().order_by('name').values('name', 'code').distinct()]
        return JsonResponse({"languages": languages}, status=200)


class StoryList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Story.objects.all()
    serializer_class = StorySerializer


class StorySentencesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request, id):
        sentences = [sentence async for sentence in Sentence.objects.filter(story=id).values('text', 'audio_key')]
        return JsonResponse({"sentences": sentences}, status=200)


class StoryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request, *args, **kwargs):
        l1 = request.data.get('l1')
        l2 = request.data.get('l2')
        level = request.data.get('level')

        stories = [s async for s in Story.objects.filter(
            native_language__name=l1,
            target_language__name=l2,
            story_level=level).values('id', 'title', 'image_url')]

        return JsonResponse(stories, safe=False)

    async def post(self, request, *args, **kwargs):
        l1 = request.data.get('l1')
        voice_id_l1 = request.data.get('voice_id_l1')
        l2 = request.data.get('l2')
        voice_id_l2 = request.data.get('voice_id_l2')
        level = request.data.get('level')
        theme = request.data.get('theme')
        characters = request.data.get('characters')
        length = request.data.get('length')
        generate_image = request.data.get('generate_image', False)

        native_language = await Language.objects.aget(name=l1)
        target_language = await Language.objects.aget(name=l2)

        voices = [v async for v
                  in Voice.objects.filter(id__in=[voice_id_l1,
                                                  voice_id_l2])
                  .values_list('id', 'supported_engines__name')]

        voice_dict = {name: min(val for n, val in voices if n == name)
                      for name, _ in voices}

        engine_l1 = list(voice_dict.values())[0]
        engine_l2 = list(voice_dict.values())[1]

        title, image_url, story_splited, story = await generate_story(l1, l2, level,
                                                                      theme, characters,
                                                                      length, generate_image)
        key = None
        if generate_image:
            key = await upload_image_to_s3(image_url, title[0])

        story = Story(title=title[0], title_translation=title[1],
                      native_language=native_language,
                      target_language=target_language,
                      story_level=level,
                      story_text=story,
                      image_url=key)

        await story.asave()

        for native_sentence, target_sentence in story_splited:
            _, task_id = await synthesize_speech_and_upload_to_s3(native_sentence, voice_id=voice_id_l1, engine=engine_l1)
            native_sentence = Sentence(text=native_sentence,
                                       language=native_language,
                                       audio_key=task_id, story=story,
                                       voice_id=voice_id_l1)
            await native_sentence.asave()

            _, task_id = await synthesize_speech_and_upload_to_s3(target_sentence, voice_id=voice_id_l2, engine=engine_l2)
            target_sentence = Sentence(text=target_sentence,
                                       language=target_language,
                                       audio_key=task_id, story=story,
                                       voice_id=voice_id_l2)
            await target_sentence.asave()

        return JsonResponse({'status': 'success'})
