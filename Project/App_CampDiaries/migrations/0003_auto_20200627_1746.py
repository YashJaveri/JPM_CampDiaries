# Generated by Django 3.0.7 on 2020-06-27 17:46

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('App_CampDiaries', '0002_auto_20200627_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camp',
            name='nextCampDate',
            field=models.DateField(blank=True, default=datetime.datetime(2020, 6, 27, 17, 46, 41, 503560, tzinfo=utc), null=True),
        ),
        migrations.AlterField(
            model_name='camp',
            name='startDate',
            field=models.DateField(blank=True, default=datetime.datetime(2020, 6, 27, 17, 46, 41, 503534, tzinfo=utc), null=True),
        ),
    ]