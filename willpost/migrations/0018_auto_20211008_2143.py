# Generated by Django 3.2.6 on 2021-10-08 21:43

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import willpost.models


class Migration(migrations.Migration):

    dependencies = [
        ('willpost', '0017_auto_20211008_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='exp_date_time',
            field=models.DateTimeField(blank=True, default=willpost.models.get_defualt_login_exp_lifetime),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_existence_confirmation',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 7, 21, 43, 57, 600877, tzinfo=utc)),
        ),
    ]
