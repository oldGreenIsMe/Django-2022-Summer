# Generated by Django 4.0.4 on 2022-08-05 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0015_alter_project_projname'),
    ]

    operations = [
        migrations.AddField(
            model_name='prototype',
            name='canvas_height',
            field=models.IntegerField(default=320),
        ),
        migrations.AddField(
            model_name='prototype',
            name='canvas_width',
            field=models.IntegerField(default=400),
        ),
    ]
