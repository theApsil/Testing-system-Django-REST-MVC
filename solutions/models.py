from django.db import models


class TestSolution(models.Model):
    test = models.ForeignKey('tests.Test', on_delete=models.PROTECT)
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)


class TaskSolution(models.Model):
    chosen_variant = models.ForeignKey('tests.AnswerVariant', on_delete=models.PROTECT)
    solution = models.ForeignKey('solutions.TestSolution', on_delete=models.CASCADE, related_name='task_solutions')

