# Generated by Django 4.0.4 on 2022-08-07 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0005_invitemessage_readstatus_invitemessage_status_and_more'),
        ('project', '0021_auto_20220807_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='startTimeRecord',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('folderId', models.AutoField(primary_key=True, serialize=False)),
                ('folderName', models.CharField(max_length=50)),
                ('isRoot', models.IntegerField(default=2)),
                ('createTime', models.DateTimeField()),
                ('lastEditTime', models.DateTimeField()),
                ('fatherFolder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.folder')),
                ('folderCreator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.user')),
                ('folderTeam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.team')),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='fileFolder',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.folder'),
        ),
    ]
