# Generated by Django 4.0.4 on 2022-08-06 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0004_invitemessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitemessage',
            name='readStatus',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='invitemessage',
            name='status',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='invitemessage',
            name='timeOrder',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invitemessage',
            name='type',
            field=models.IntegerField(default=1),
        ),
    ]
