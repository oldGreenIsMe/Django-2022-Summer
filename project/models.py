from django.db import models
from team.models import User, Team
from utils import storage
from django.dispatch import receiver
from django.db.models.signals import pre_delete


# 项目类
class Project(models.Model):
    projId = models.AutoField(primary_key=True)
    projName = models.CharField(max_length=50)
    projCreator = models.ForeignKey(to=User, null=False, blank=False, on_delete=models.CASCADE, related_name='creator')
    projTeam = models.ForeignKey(to=Team, null=False, blank=False, on_delete=models.CASCADE)
    projInfo = models.TextField(default='暂无简介')
    startTime = models.CharField(max_length=20, null=True, blank=True)
    endTime = models.CharField(max_length=20, null=True, blank=True)
    # 用于判断是否被删除到回收站中 1-未被删除 2-回收站中
    status = models.IntegerField(default=1)
    # 记录删除的用户（ID）及删除时间
    deletePerson = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='deletePerson')
    deleteTime = models.CharField(max_length=20, null=True, blank=True)
    deleteTimeRecord = models.DateTimeField(null=True, blank=True)
    photo = models.ImageField(upload_to='projImg', default='projImg/default.png', storage=storage.ImageStorage())


# 文档类
class File(models.Model):
    fileId = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=50)
    fileCreator = models.ForeignKey(to=User, null=False, blank=False, on_delete=models.CASCADE,
                                    related_name='fileCreator')
    content = models.TextField(null=True, blank=True)
    create = models.CharField(max_length=25, null=True, blank=True)
    lastEditTime = models.CharField(max_length=20, null=True, blank=True)
    lastEditUser = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE,
                                     related_name='lastEditUser')
    lastEditTimeRecord = models.DateTimeField(auto_now=True)
    projectId = models.ForeignKey(to=Project, null=False, blank=False, on_delete=models.CASCADE)
    edit_file = models.ManyToManyField(User, through='UserFile')


class FileImage(models.Model):
    file = models.ForeignKey(to=File, null=False, blank=False, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='fileImg', storage=storage.ImageStorage)


# 原型类
class Prototype(models.Model):
    prototypeId = models.AutoField(primary_key=True)
    projectId = models.ForeignKey(to=Project, null=False, blank=False, on_delete=models.CASCADE)
    protoName = models.CharField(max_length=50, unique=True, default='proto_default')
    protoCreator = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE)
    protoContent = models.TextField(null=True, blank=True, default='[]')
    protoPhoto = models.TextField(null=True, blank=True)
    canvas_width = models.IntegerField(default=400)
    canvas_height = models.IntegerField(default=320)


class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)     # 0不在编辑，1正在编辑


@receiver(pre_delete, sender=Project)
def projPhotoDelete(instance, **kwargs):
    instance.photo.delete(False)