# Generated by Django 3.2.6 on 2021-10-08 21:44

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('willpost', '0018_auto_20211008_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_existence_confirmation',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 7, 21, 44, 3, 408362, tzinfo=utc)),
        ),
    ]
