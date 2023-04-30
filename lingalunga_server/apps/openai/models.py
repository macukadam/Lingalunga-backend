from django.db import models
from lingalunga_server.apps.s3.models import Voice
from lingalunga_server.apps.accounts.models import User

# Create your models here.


class Language(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StoryParams(models.Model):
    native_language = models.CharField(max_length=50)
    target_language = models.CharField(max_length=50)
    characters = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    theme = models.CharField(max_length=50)
    selected_level = models.CharField(max_length=2, default='a1')
    generate_image = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Story(models.Model):
    class Level(models.TextChoices):
        A1 = 'a1'
        A2 = 'a2'
        B1 = 'b1'
        B2 = 'b2'
        C1 = 'c1'
        C2 = 'c2'

    title = models.CharField(max_length=200)
    title_translation = models.CharField(max_length=200)
    native_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name='native_language')
    target_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name='target_language')
    created_at = models.DateTimeField(auto_now_add=True)
    story_level = models.CharField(choices=Level.choices, max_length=2)
    image_url = models.CharField(max_length=1000, null=True, blank=True)
    story_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Sentence(models.Model):
    text = models.TextField()
    audio_key = models.CharField(max_length=100, null=True, blank=True)
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name='story')
    voice = models.ForeignKey(
        Voice, on_delete=models.CASCADE, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
