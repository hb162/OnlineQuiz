# Generated by Django 3.0.8 on 2020-10-23 15:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_auto_20201012_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='shuffle_answers',
            field=models.CharField(choices=[('1', 'shuffle'), ('0', 'not shuffle')], default=0, max_length=1),
        ),
        migrations.AlterField(
            model_name='quizcopy1',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 23, 22, 7, 59, 695622)),
        ),
        migrations.AlterField(
            model_name='quizcopy2',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 23, 22, 7, 59, 696619)),
        ),
    ]