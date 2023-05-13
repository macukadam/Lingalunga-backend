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


class Word(models.Model):
    text = models.CharField(max_length=255)
    dep = models.CharField(max_length=255)
    head = models.CharField(max_length=255)
    lemma = models.CharField(max_length=255)
    pos = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)
    is_alpha = models.BooleanField()
    is_stop = models.BooleanField()
    is_punct = models.BooleanField()
    is_space = models.BooleanField()
    is_digit = models.BooleanField()
    is_currency = models.BooleanField()
    is_quote = models.BooleanField()
    is_bracket = models.BooleanField()
    is_left_punct = models.BooleanField()
    is_right_punct = models.BooleanField()
    is_title = models.BooleanField()
    is_upper = models.BooleanField()
    is_lower = models.BooleanField()
    is_oov = models.BooleanField()
    is_sent_start = models.BooleanField()
    is_sent_end = models.BooleanField()
    index = models.IntegerField()
    idx = models.IntegerField()
    text_with_ws = models.CharField(max_length=255)
    sentiment = models.FloatField()
    ent_type = models.CharField(max_length=255)
    ent_iob = models.CharField(max_length=255)
    ent_kb_id = models.CharField(max_length=255, blank=True, null=True)
    ent_id = models.CharField(max_length=255, blank=True, null=True)
    childeren = models.JSONField()
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)
