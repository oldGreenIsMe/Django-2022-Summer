# Generated by Django 3.2.5 on 2022-08-07 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0019_auto_20220807_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='copy_num',
            field=models.IntegerField(default=0),
        ),
    ]
