from utils import storage
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete


class Team(models.Model):
    teamid = models.AutoField(primary_key=True)
    teamname = models.CharField(max_length=100, default='')


class User(models.Model):
    objects = models.Manager
    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, default='')
    truename = models.CharField(max_length=100, default='')
    password = models.CharField(max_length=100, default='')
    photo = models.ImageField(upload_to='img', default='img/default_photo.png', storage=storage.ImageStorage())
    team_belonged = models.ManyToManyField(Team, through='UserTeam')
    email = models.EmailField(unique=True)


class UserTeam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    permission = models.IntegerField(default=0)  # 0为普通成员，1为管理员, 2为创始者


class InviteMessage(models.Model):
    inviteId = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='inviter_message')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_message')


@receiver(pre_delete, sender=User)
def userPhotoDelete(instance, **kwargs):
    instance.photo.delete(False)
