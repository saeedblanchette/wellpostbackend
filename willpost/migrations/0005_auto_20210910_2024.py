# Generated by Django 3.2.6 on 2021-09-10 20:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('willpost', '0004_auto_20210908_2335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='media',
        ),
        migrations.RemoveField(
            model_name='post',
            name='post_type',
        ),
        migrations.RemoveField(
            model_name='post',
            name='text',
        ),
        migrations.AddField(
            model_name='post',
            name='file',
            field=models.FileField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='post',
            name='media_type',
            field=models.CharField(choices=[('VIDEO', 'Video'), ('AUDIO', 'Audio')], default='AUDIO', max_length=50, verbose_name='media type'),
        ),
        migrations.AlterField(
            model_name='user',
            name='exp_date_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 9, 10, 20, 24, 59, 635563, tzinfo=utc)),
        ),
        migrations.DeleteModel(
            name='Media',
        ),
    ]