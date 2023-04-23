from django.db import models
from lingalunga_server.apps.s3.models import Voice

# Create your models here.


class Language(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Story(models.Model):
    class Level(models.TextChoices):
        A1 = 'a1'
        A2 = 'a2'
        B1 = 'b1'
        B2 = 'b2'
        C1 = 'c1'
        C2 = 'c2'

    title = models.CharField(max_length=200)
    native_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name='native_language')
    target_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name='target_language')
    created_at = models.DateTimeField(auto_now_add=True)
    story_level = models.CharField(choices=Level.choices, max_length=2)
    image_url = models.CharField(max_length=1000, null=True, blank=True)

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
