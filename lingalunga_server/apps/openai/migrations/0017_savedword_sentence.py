# Generated by Django 4.2 on 2023-05-15 12:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('openai', '0016_savedword_completedstory'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedword',
            name='sentence',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='openai.sentence'),
            preserve_default=False,
        ),
    ]