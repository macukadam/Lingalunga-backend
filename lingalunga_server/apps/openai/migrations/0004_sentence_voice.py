# Generated by Django 4.2 on 2023-04-17 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('s3', '0002_voice_supported_engines'),
        ('openai', '0003_delete_storyline_story_story_level_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentence',
            name='voice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='s3.voice'),
        ),
    ]