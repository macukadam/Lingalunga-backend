from django.db import models


class Engine(models.Model):
    ENGINE_CHOICES = [
        ('neural', 'Neural'),
        ('standard', 'Standard'),
    ]

    name = models.CharField(max_length=10, choices=ENGINE_CHOICES)

    def __str__(self):
        return self.name


class Voice(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    id = models.CharField(max_length=50, primary_key=True)
    language_code = models.CharField(max_length=10)
    language_name = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    supported_engines = models.ManyToManyField(Engine)

    def __str__(self):
        return self.name
