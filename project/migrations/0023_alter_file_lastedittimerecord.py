# Generated by Django 4.0.4 on 2022-08-08 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0022_project_starttimerecord_folder_file_filefolder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='lastEditTimeRecord',
            field=models.DateTimeField(),
        ),
    ]
