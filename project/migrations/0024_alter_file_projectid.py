# Generated by Django 4.0.4 on 2022-08-08 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0023_alter_file_lastedittimerecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='projectId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.project'),
        ),
    ]