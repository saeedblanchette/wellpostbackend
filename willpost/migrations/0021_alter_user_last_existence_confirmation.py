# Generated by Django 3.2.6 on 2021-10-08 21:46

from django.db import migrations, models
import willpost.models


class Migration(migrations.Migration):

    dependencies = [
        ('willpost', '0020_alter_user_last_existence_confirmation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_existence_confirmation',
            field=models.DateTimeField(default=willpost.models.get_default_last_existence_confirmation),
        ),
    ]
