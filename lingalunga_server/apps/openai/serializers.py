from rest_framework import serializers
from .models import Story, Language, Sentence


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
