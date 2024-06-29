from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class StudyGroup(models.Model):
    study_group_name = models.CharField(max_length=100)
    study_group_id = models.AutoField(primary_key=True)
    study_group_img_link = models.URLField(max_length=200)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='study_groups')

    def __str__(self):
        return self.study_group_name