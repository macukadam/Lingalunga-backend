import json
import httpx
from django.db.models import F
from .serializers import StorySerializer, process_word_json
from rest_framework import generics
from adrf import views
from lingalunga_server.apps.openai.tasks import generate_story
from rest_framework import permissions
from django.http import JsonResponse
from .models import Story, Sentence, Language, StoryParams
from lingalunga_server.apps.s3.models import Voice
from lingalunga_server.apps.s3.tasks import \
    synthesize_speech_and_upload_to_s3, upload_image_to_s3
from lingalunga_server.celery import app
import asyncio

TIMEOUT = 240


@app.task
def generate_words(id):
    asyncio.run(call_word_generation(id))


async def call_word_generation(id):
    url = "http://18.184.139.204/tokenize"

    sentences = [s async for s in Sentence.objects.filter(story_id=id)]

    for sentence in sentences:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            data = {"sentence": sentence.text,
                    'language': sentence.language.code}
            response = await client.post(url, json=data)
            body = response.json()
            print(body)

            await process_word_json(body, sentence)


async def save_story(l1, l2, level, theme, characters, length, generate_image):
    native_language = await Language.objects.aget(name=l1)
    target_language = await Language.objects.aget(name=l2)

    v1 = Voice.objects.filter(language_name__icontains=l1,
                              supported_engines__name='natural').values_list(
        'id', 'supported_engines__name').order_by('?').first()

    if not v1:
        v1 = Voice.objects.filter(language_name__icontains=l1).values_list(
            'id', 'supported_engines__name').order_by('?').first()

    v2 = Voice.objects.filter(language_name__icontains=l2,
                              supported_engines__name='natural').values_list(
        'id', 'supported_engines__name').order_by('?').first()

    if not v2:
        v2 = Voice.objects.filter(language_name__icontains=l2).values_list(
            'id', 'supported_engines__name').order_by('?').first()

    voices = [v1, v2]

    voice_dict = {name: min(val for n, val in voices if n == name)
                  for name, _ in voices}

    engine_l1 = list(voice_dict.values())[0]
    engine_l2 = list(voice_dict.values())[1]

    print("Generating story...")
    title, image_url, story_splited, story = await generate_story(l1, l2, level,
                                                                  theme, characters,
                                                                  length, generate_image)
    print("Story generated")
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

    print("Creating voice objects...")
    for native_sentence, target_sentence in story_splited:
        _, task_id = await synthesize_speech_and_upload_to_s3(native_sentence, voice_id=v1[0], engine=engine_l1)
        native_sentence = Sentence(text=native_sentence,
                                   language=native_language,
                                   audio_key=task_id, story=story,
                                   voice_id=v1[0])
        await native_sentence.asave()

        _, task_id = await synthesize_speech_and_upload_to_s3(target_sentence, voice_id=v2[0], engine=engine_l2)
        target_sentence = Sentence(text=target_sentence,
                                   language=target_language,
                                   audio_key=task_id, story=story,
                                   voice_id=v2[0])
        await target_sentence.asave()

    print("Voice objects created")

    return story


class StoryRequestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request):
        print("POST request received")
        print(request.data)
        user = request.user

        story_params = StoryParams(**request.data, user=user)
        story_params.save()

        if user.is_superuser:
            l1 = request.data['native_language']
            l2 = request.data['target_language']
            level = request.data['selected_level'].lower()
            characters = request.data['characters']
            theme = request.data['theme']
            length = 10
            generate_image = request.data['generate_image']

            story = await save_story(l1, l2, level, theme, characters, length,
                                     generate_image)

            call_word_generation.delay(story.sentence_set.all())

        else:
            return JsonResponse({"error": "Your account cannot create a new story "}, status=403)

        return JsonResponse({'success': 'OK'}, status=201)


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
        swiped = request.data.get('swiped')
        sentences = [sentence async for sentence in Sentence.objects.filter(story=id).values('text', 'audio_key')]

        if swiped:
            sentences[:-1:2], sentences[1::2] = sentences[1::2], sentences[:-1:2]

        return JsonResponse({"sentences": sentences}, status=200)


class WordInsertionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request):
        url = "http://18.184.139.204/tokenize"
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(url, json=request.data)
            body = response.json()

            await process_word_json(body, 0)

            return JsonResponse({"success": "OK"}, status=200)


class WordInsertionByStoryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request, id):
        url = "http://18.184.139.204/tokenize"
        sentences = Sentence.objects.filter(
            story=id)

        for sentence in sentences:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                data = {"sentence": sentence.text,
                        'language': sentence.language.code}
                response = await client.post(url, json=data)
                body = response.json()
                print(body)

                await process_word_json(body, sentence)

        return JsonResponse({"success": "OK"}, status=200)


class StoryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request, *args, **kwargs):
        l1 = request.data.get('l1')
        l2 = request.data.get('l2')
        level = request.data.get('level')
        reverse = request.data.get('reverse')

        if reverse:
            stories = [s async for s in Story.objects.filter(
                native_language__name=l2,
                target_language__name=l1,
                story_level=level).values('id',
                                          'image_url',
                                          story_title=F('title_translation'))]

        else:
            stories = [s async for s in Story.objects.filter(
                native_language__name=l1,
                target_language__name=l2,
                story_level=level).values('id',
                                          'image_url',
                                          story_title=F('title'))]

        return JsonResponse(stories, safe=False)
