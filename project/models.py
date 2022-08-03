from django.db import models
from team.models import *
from utils import storage


# 项目类
class Project(models.Model):
    projId = models.AutoField(primary_key=True)
    projName = models.CharField(max_length=50, unique=True)
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
    photo = models.ImageField(upload_to='projImg', default='projImg/default.png', storage=storage.ImageStorage())


# 文档类
class File(models.Model):
    fileId = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=50, unique=True)
    fileCreator = models.ForeignKey(to=User, null=False, blank=False, on_delete=models.CASCADE,
                                    related_name='fileCreator')
    content = models.TextField(null=True, blank=True)
    create = models.CharField(max_length=25, null=True, blank=True)
    lastEditTime = models.CharField(max_length=20, null=True, blank=True)
    lastEditUser = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE,
                                     related_name='lastEditUser')
    projectId = models.ForeignKey(to=Project, null=False, blank=False, on_delete=models.CASCADE)


# 原型类
class Prototype(models.Model):
    prototypeId = models.AutoField(primary_key=True)
    projectId = models.ForeignKey(to=Project, null=False, blank=False, on_delete=models.CASCADE)
    protoName = models.CharField(max_length=50, unique=True, default='proto_default')
    protoCreator = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE)
    protoFile = models.FileField(upload_to='projProto', default='projProto/proto_default.json',
                                 storage=storage.ProtoStorage)
