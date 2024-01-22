from django import db
from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=64)


class Task(models.Model):
    text = models.TextField()
    topic = models.ForeignKey('tests.Topic', on_delete=models.PROTECT)


class AnswerVariant(models.Model):
    text = models.TextField()
    task = models.ForeignKey('tests.Task', on_delete=models.CASCADE, related_name='variants')
    is_correct = models.BooleanField()


class Test(models.Model):

    name = models.CharField(max_length=64)
    tasks = models.ManyToManyField('tests.Task', related_name='tests')





