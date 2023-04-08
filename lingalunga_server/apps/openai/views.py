from .tasks import generate_story
from django.http import JsonResponse

# Create your views here.


def generate_dummy_story(request):
    print("Calling dummy task")
    task = generate_story.apply_async(countdown=0)
    response_data = {'task_id': task.id}
    return JsonResponse(response_data)
