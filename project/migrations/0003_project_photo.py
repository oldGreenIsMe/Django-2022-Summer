# Generated by Django 3.2.5 on 2022-08-02 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_project_endtime_project_projinfo_project_starttime'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='photo',
            field=models.ImageField(default='team_photo/default.png', upload_to='team_photo'),
        ),
    ]
