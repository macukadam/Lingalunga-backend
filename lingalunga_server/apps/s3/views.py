from .models import Voice
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from rest_framework import status, permissions
from rest_framework.response import Response
from dotenv import load_dotenv
from lingalunga_server.settings import redis_pool
from adrf import views
import aioboto3
from lingalunga_server.apps.openai.models import Language
from lingalunga_server.apps.s3.models import Engine
import redis.asyncio as redis
import os

load_dotenv()

CACHE_TIME = os.getenv("CACHE_TIME", 3600)
BUCKET_NAME = os.getenv("BUCKET_NAME", "lingalunga")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-central-1")


class GetObjectUrls(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request):
        keys = request.data.get('keys', [])

        urls = []
        keys_to_check = []
        redis_client = redis.Redis(connection_pool=redis_pool)

        for key in keys:
            cached_url = await redis_client.get(key)
            if cached_url:
                print("Getting cached url")
                urls.append(cached_url)
            else:
                keys_to_check.append(key)

        async with aioboto3.Session().client('s3', region_name=AWS_DEFAULT_REGION) as s3:
            for key in keys_to_check:
                print("Generating permanent url")
                url = await s3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={'Bucket': BUCKET_NAME, 'Key': key},
                    ExpiresIn=CACHE_TIME)
                await redis_client.setex(key, CACHE_TIME, url)
                urls.append(url)

        await redis_client.close()
        await redis_client.connection_pool.disconnect()

        return Response({"urls": urls}, status=status.HTTP_200_OK)


class Voices(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        voices = Voice.objects.all()
        return JsonResponse(list(voices.values('gender', 'id', 'language_code', 'language_name', 'name', 'supported_engines')), safe=False)

    def post(self, request):
        data = JSONParser().parse(request)
        response_data = []

        for voice_data in data:
            language = voice_data['LanguageName'].split(' ')[-1]
            code = voice_data['LanguageCode'].split('-')[0]
            Language.objects.get_or_create(name=language, code=code)

            supported_engines = [Engine.objects.get_or_create(
                name=engine)[0] for engine in voice_data['SupportedEngines']]
            voice, created = Voice.objects.update_or_create(
                id=voice_data['Id'],
                defaults={
                    'gender': voice_data['Gender'],
                    'language_code': voice_data['LanguageCode'],
                    'language_name': voice_data['LanguageName'],
                    'name': voice_data['Name'],
                }
            )

            voice.supported_engines.set(supported_engines)
            response_data.append({
                'id': voice.id,
                'created': created,
                'updated': not created
            })

        return JsonResponse(response_data, safe=False, status=200)
