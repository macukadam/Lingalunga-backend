from .models import Voice
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from rest_framework import status, permissions
from rest_framework.response import Response
from dotenv import load_dotenv
from lingalunga_server.settings import redis_client
from adrf import views
import aioboto3
from lingalunga_server.apps.openai.models import Language

BUCKET_NAME = 'lingagunga'

load_dotenv()


class GetAllFiles(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request):
        async with aioboto3.Session().client('s3') as s3:
            response = await s3.list_objects_v2(Bucket=BUCKET_NAME)

            obj_out = {}
            for obj in response['Contents']:
                folder, file = obj['Key'].split("/")
                obj_out[folder] = obj_out.get(folder, []) + [file]

        return Response(obj_out, status=status.HTTP_200_OK)


class GetObjectUrls(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request):
        # Get a list of keys from the query parameters
        keys = request.GET.getlist('key')
        print(keys)

        urls = []
        async with aioboto3.Session().client('s3') as s3:
            for key in keys:
                print(key)
                # Try to get the URL from the Redis cache
                cached_url = await redis_client.get(key)
                print(cached_url)

                if cached_url:
                    url = cached_url.decode()
                else:
                    print("Not in cache")
                    # Generate the URL and store it in the Redis cache
                    url = await s3.generate_presigned_url(
                        ClientMethod='get_object',
                        Params={'Bucket': BUCKET_NAME, 'Key': key},
                        ExpiresIn=3600  # 1 hour expiration
                    )
                    # Cache the URL for 1 hour
                    await redis_client.setex(key, 3600, url)

                urls.append(url)

        return Response({"urls": urls}, status=status.HTTP_200_OK)


class Voices(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        voices = Voice.objects.all()
        return JsonResponse(list(voices.values()), safe=False)

    def post(self, request):
        data = JSONParser().parse(request)
        response_data = []

        for voice_data in data:
            language = voice_data['LanguageName'].split(' ')[-1]
            Language.objects.get_or_create(name=language)

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
