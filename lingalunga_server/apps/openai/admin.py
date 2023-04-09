from django.contrib import admin
from lingalunga_server.apps.openai.models import Language, Story, Sentence


# Register your models here.

admin.site.register(Language)
admin.site.register(Sentence)
admin.site.register(Story)
