from rest_framework import status, permissions, views
from rest_framework.response import Response
import boto3
from dotenv import load_dotenv

BUCKET_NAME = 'lingagunga'

load_dotenv()
s3 = boto3.client('s3')


class GetAllFiles(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)

        # objects = [{'key': obj['Key']} for obj in response['Contents']]

        obj_out = {}
        for obj in response['Contents']:
            folder, file = obj['Key'].split("/")
            obj_out[folder] = obj_out.get(folder, []) + [file]

        return Response(obj_out, status=status.HTTP_200_OK)


class GetObjectUrl(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        key = request.GET.get('key')

        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=3600  # 1 hour expiration
        )

        return Response({"url": url}, status=status.HTTP_200_OK)
