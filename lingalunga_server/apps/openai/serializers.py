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


async def process_word_json(data, parent=None):
    words = []
    for item in data:
        print('Word is ', item.get('text'))
        word = Word(
            text=item.get('text'),
            dep=item.get('dep'),
            head=item.get('head'),
            lemma=item.get('lemma'),
            pos=item.get('pos'),
            tag=item.get('tag'),
            is_alpha=item.get('is_alpha'),
            is_stop=item.get('is_stop'),
            is_punct=item.get('is_punct'),
            is_space=item.get('is_space'),
            is_digit=item.get('is_digit'),
            is_currency=item.get('is_currency'),
            is_quote=item.get('is_quote'),
            is_bracket=item.get('is_bracket'),
            is_left_punct=item.get('is_left_punct'),
            is_right_punct=item.get('is_right_punct'),
            is_title=item.get('is_title'),
            is_upper=item.get('is_upper'),
            is_lower=item.get('is_lower'),
            is_oov=item.get('is_oov'),
            is_sent_start=item.get('is_sent_start'),
            is_sent_end=item.get('is_sent_end'),
            index=item.get('index'),
            idx=item.get('idx'),
            text_with_ws=item.get('text_with_ws'),
            sentiment=item.get('sentiment'),
            ent_type=item.get('ent_type'),
            ent_iob=item.get('ent_iob'),
            ent_kb_id=item.get('ent_kb_id'),
            ent_id=item.get('ent_id'),
        )
        await word.asave()
        print('Word saved')
        words.append(word)

    for idx, item in enumerate(data):
        parent_word = words[idx]
        for index in item.get('children', []):
            print('Index is ', index)
            pass
            index = int(index)
            child_word = words[index]
            await child_word.parent.aadd(parent_word)
