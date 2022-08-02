from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.models import *


@csrf_exempt
def createProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    projName = request.POST.get('proj_name')
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    projTeam = Team.objects.get(teamid=request.POST.get('team_id'))
    projInfo = request.POST.get('proj_info')
    if projInfo is None:
        projInfo = "暂无简介"
    startTime = request.POST.get('start_time')
    endTime = request.POST.get('end_time')
    projects = Project.objects.filter(projName=projName, projTeam=projTeam)
    if projects.exists():
        return JsonResponse({'errno': 400001, 'msg': '项目名称重复'})
    project = Project(projName=projName, projCreator=user, projTeam=projTeam, projInfo=projInfo, startTime=startTime,
                      endTime=endTime, deletePerson=None, deleteTime=None)
    project.save()
    return JsonResponse({'errno': 0, 'msg': '项目创建成功'})


@csrf_exempt
def deleteProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    projId = request.POST.get('proj_id')
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    time = request.POST.get('time')
    projects = Project.objects.filter(projId=projId)
    if not projects.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    project = projects.first()
    project.status = 2
    project.deletePerson = user
    project.deleteTime = time
    project.save()
    return JsonResponse({'errno': 0, 'msg': '项目已移入回收站'})


@csrf_exempt
def clearProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    projId = request.POST.get('proj_id')
    projects = Project.objects.filter(projId=projId)
    if not projects.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    project = projects.first()
    project.delete()
    return JsonResponse({'errno': 0, 'msg': '项目删除成功'})


@csrf_exempt
def recoverProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 500001, 'msg': '请登录'})
    projid = request.POST.get('proj_id')
    projs = Project.objects.filter(projId=projid)
    if not projs.exists():
        return JsonResponse({'errno': 300001, 'msg': '项目不存在'})
    proj = projs.first()
    team = proj.projTeam
    member_set = team.user_set.all()
    if not member_set.filter(userid=users.first().userid).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    proj.status = 1
    proj.deletePerson = None
    proj.deleteTime = None
    proj.save()
    return JsonResponse({'errno': 0, 'msg': '恢复项目成功'})


@csrf_exempt
def renameProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 500001, 'msg': '请登录'})
    projid = request.POST.get('proj_id')
    projs = Project.objects.filter(projId=projid)
    if not projs.exists():
        return JsonResponse({'errno': 300001, 'msg': '项目不存在'})
    newname = request.POST.get('new_name')
    if newname is None or newname == '':
        return JsonResponse({'errno': 400003, 'msg': '名称不能为空'})

    Project.objects.filter(projId=projid).update(projName=newname)
    return JsonResponse({'errno': 0, 'msg': '修改成功'})


@csrf_exempt
def detailProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 500001, 'msg': '请登录'})

    projid = request.POST.get('proj_id')
    projs = Project.objects.filter(projId=projid)
    if not projs.exists():
        return JsonResponse({'errno': 300001, 'msg': '项目不存在'})
    proj = projs.first()
    proj_name = proj.projName
    creator = proj.projCreator
    info = proj.projInfo
    start = proj.startTime
    end = proj.endTime
    team = proj.projTeam
    member_set = team.user_set.all()
    if not member_set.filter(userid=users.first().userid).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限查看该项目'})
    members = []
    for i in member_set:
        members.append(
            {
                'userid': i.userid,
                'username': i.username,
                'truename': i.truename,
                'password': i.password,
                'photo': i.photo,
                'email': i.email
            }
        )
    print(members)
    return JsonResponse({'errno': 0, 'msg': '查看成功', 'proj_name': proj_name, 'proj_creator': creator.username,
                         'proj_start': start, 'proj_end': end, 'proj_team': team.teamname,
                         'proj_info': info, 'members': members})
