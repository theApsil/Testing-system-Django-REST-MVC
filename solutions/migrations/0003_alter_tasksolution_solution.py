# Generated by Django 5.0.1 on 2024-06-29 00:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solutions', '0002_init'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasksolution',
            name='solution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_solutions', to='solutions.testsolution'),
        ),
    ]
