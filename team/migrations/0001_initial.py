# Generated by Django 4.0.4 on 2022-08-01 11:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('teamid', models.AutoField(primary_key=True, serialize=False)),
                ('teamname', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('userid', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(default='', max_length=100)),
                ('truename', models.CharField(default='', max_length=100)),
                ('password', models.CharField(default='', max_length=100)),
                ('photo', models.ImageField(default='img/default_photo.png', upload_to='img')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='UserTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.IntegerField(default=0)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.user')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='team_belonged',
            field=models.ManyToManyField(through='team.UserTeam', to='team.team'),
        ),
    ]
