# Generated by Django 4.2 on 2023-04-22 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openai', '0004_sentence_voice'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='code',
            field=models.CharField(default='', max_length=2),
            preserve_default=False,
        ),
    ]
