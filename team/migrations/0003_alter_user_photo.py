# Generated by Django 4.0.4 on 2022-08-03 03:56

from django.db import migrations, models
import utils.storage


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(default='img/default_photo.png', storage=utils.storage.ImageStorage(), upload_to='img'),
        ),
    ]
