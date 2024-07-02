from django.db import models
from django.conf import settings


class StudyGroup(models.Model):
    study_group_name = models.CharField(max_length=100)
    study_group_id = models.AutoField(primary_key=True)
    study_group_img_link = models.URLField(max_length=200)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='teacher_groups'
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='study_groups')

    def __str__(self):
        return self.study_group_name


class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    cover_image = models.URLField(max_length=200)
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='tests')

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    image = models.URLField(max_length=200, blank=True, null=True)  # новое поле для изображения

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.question.text}'


class UserTestStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    grade = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.test.title} - {"Completed" if self.is_completed else "Not Completed"}'
