# Generated by Django 4.0.4 on 2022-08-08 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0024_alter_file_projectid'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='preview_status',
            field=models.IntegerField(default=0),
        ),
    ]