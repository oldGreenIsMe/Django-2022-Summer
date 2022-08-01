from team.models import *


# 项目类
class Project(models.Model):
    projId = models.AutoField(primary_key=True)
    projName = models.CharField(max_length=50, unique=True)
    projCreator = models.ForeignKey(to=User, null=False, blank=False, on_delete=models.CASCADE, related_name='projCreator')
    projTeam = models.ForeignKey(to=Team, null=False, blank=False, on_delete=models.CASCADE)
    # 用于判断是否被删除到回收站中 1-未被删除 2-回收站中
    status = models.IntegerField(default=1)
    # 记录删除的用户（ID）及删除时间
    deletePerson = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.SET_NULL, related_name='deletePerson')
    deleteTime = models.CharField(max_length=20, null=True, blank=True)


# 文档类
class File(models.Model):
    fileId = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=50, unique=True)
    fileCreator = models.ForeignKey(to=User, null=False, blank=False, on_delete=models.CASCADE)
    projectId = models.ForeignKey(to=Project, null=False, blank=False, on_delete=models.CASCADE)


# 原型类（具体存什么东西还没定，等前端确定）
class Prototype(models.Model):
    prototypeId = models.AutoField(primary_key=True)
    projectId = models.ForeignKey(to=Project, null=False, blank=False, on_delete=models.CASCADE)
