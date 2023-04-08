from rest_framework import status, permissions
from rest_framework.response import Response
import boto3
from dotenv import load_dotenv
from lingalunga_server.settings import redis_client
from django.http import JsonResponse
from .tasks import dummy_task
from adrf import views

BUCKET_NAME = 'lingagunga'

load_dotenv()
s3 = boto3.client('s3')


class GetAllFiles(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)

        obj_out = {}
        for obj in response['Contents']:
            folder, file = obj['Key'].split("/")
            obj_out[folder] = obj_out.get(folder, []) + [file]

        return Response(obj_out, status=status.HTTP_200_OK)


class GetObjectUrls(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get a list of keys from the query parameters
        keys = request.GET.getlist('key')
        print(keys)

        urls = []
        for key in keys:
            print(key)
            # Try to get the URL from the Redis cache
            cached_url = redis_client.get(key)
            print(cached_url)

            if cached_url:
                url = cached_url.decode()
            else:
                print("Not in cache")
                # Generate the URL and store it in the Redis cache
                url = s3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={'Bucket': BUCKET_NAME, 'Key': key},
                    ExpiresIn=3600  # 1 hour expiration
                )
                # Cache the URL for 1 hour
                redis_client.setex(key, 3600, url)

            urls.append(url)

        return Response({"urls": urls}, status=status.HTTP_200_OK)


def call_dummy_task(request):
    print("Calling dummy task")
    task = dummy_task.apply_async(countdown=0)
    response_data = {'task_id': task.id}
    return JsonResponse(response_data)
