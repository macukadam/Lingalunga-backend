import json
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import Story, Language, Sentence, Word


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class StorySerializer(serializers.ModelSerializer):
    # native_language = LanguageSerializer()
    # target_language = LanguageSerializer()
    # story = SentenceSerializer(many=True)

    class Meta:
        model = Story
        fields = '__all__'


async def process_word_json(data, sentence):
    words = []
    for item in data:
        word = Word(
            *item,
            sentence=sentence
        )
        await word.asave()
        words.append(word)
