# Generated by Django 5.0.1 on 2024-06-29 00:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0001_init'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answervariant',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='tests.task'),
        ),
        migrations.AlterField(
            model_name='test',
            name='tasks',
            field=models.ManyToManyField(related_name='tests', to='tests.task'),
        ),
    ]