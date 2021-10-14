# Generated by Django 3.2.6 on 2021-10-08 21:40

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('willpost', '0016_auto_20211008_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='exp_date_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 10, 9, 21, 40, 13, 95407, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_existence_confirmation',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 7, 21, 40, 13, 96398, tzinfo=utc)),
        ),
    ]
