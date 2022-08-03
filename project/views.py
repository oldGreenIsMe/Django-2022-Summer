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
    if projInfo is None or projInfo == "":
        projInfo = "暂无简介"
    startTime = request.POST.get('start_time')
    endTime = request.POST.get('end_time')
    projects = Project.objects.filter(projName=projName, projTeam=projTeam)
    if projects.exists():
        return JsonResponse({'errno': 400001, 'msg': '项目名称重复'})
    project = Project(projName=projName, projCreator=user, projTeam=projTeam, projInfo=projInfo, startTime=startTime,
                      endTime=endTime, deletePerson=None, deleteTime=None)
    project.save()
    return JsonResponse({'errno': 0, 'msg': '项目创建成功', 'proj_id': project.projId})


@csrf_exempt
def modifyProjPhoto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    projId = request.POST.get('proj_id')
    projects = Project.objects.filter(projId=projId)
    if not projects.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    project = projects.first()
    photo = request.FILES.get('photo')
    project.photo = photo
    project.save()
    return JsonResponse({'errno': 0, 'msg': '图片修改成功'})


@csrf_exempt
def modifyProjInfo(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    projId = request.POST.get('proj_id')
    projects = Project.objects.filter(projId=projId)
    if not projects.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    project = projects.first()
    judge = int(request.POST.get('judge'))
    msg = '修改成功'
    if judge == 1:
        info = request.POST.get('info')
        project.projInfo = info
        msg = '项目简介' + msg
    elif judge == 2:
        start = request.POST.get('start')
        project.startTime = start
        msg = '项目开始时间' + msg
    else:
        end = request.POST.get('end')
        project.endTime = end
        msg = '项目结束时间' + msg
    project.save()
    return JsonResponse({'errno': 0, 'msg': msg})


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
                'photo': i.photo.url,
                'email': i.email
            }
        )
    print(members)
    return JsonResponse({'errno': 0, 'msg': '查看成功', 'proj_name': proj_name, 'proj_creator': creator.username,
                         'proj_start': start, 'proj_end': end, 'proj_team': team.teamname,
                         'proj_info': info, 'members': members, 'proj_photo': proj.photo.url})


@csrf_exempt
def create_proto(request):
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
    proto_name = request.POST.get('proto_name')
    protos = Prototype.objects.filter(protoName=proto_name, projectId=projid)
    if protos.exists():
        return JsonResponse({'errno': 400001, 'msg': '设计原型名称重复'})
    proto = Prototype(projectId=proj, protoName=proto_name, protoCreator=users.first())
    proto.save()
    return JsonResponse({'errno': 0, 'msg': '创建成功', 'proto_id': proto.prototypeId})


@csrf_exempt
def upload_proto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 500001, 'msg': '请登录'})
    proto_id = request.POST.get('proto_id')
    protos = Prototype.objects.filter(prototypeId=proto_id)
    if not protos.exists():
        return JsonResponse({'errno': 300001, 'msg': '设计原型不存在'})
    proto_file = request.FILES.get('proto_file')
    proto = protos.first()
    old_file = proto.protoFile.url
    proto.protoFile = proto_file
    proto.save()
    return JsonResponse({'errno': 0, 'msg': '上传成功'})


@csrf_exempt
def get_proto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 500001, 'msg': '请登录'})
    proto_id = request.POST.get('proto_id')
    protos = Prototype.objects.filter(prototypeId=proto_id)
    if not protos.exists():
        return JsonResponse({'errno': 300001, 'msg': '设计原型不存在'})
    proto = protos.first()
    proto_file = proto.protoFile.url
    return JsonResponse({'errno': 0, 'msg': '获取成功', 'proto_file': proto_file})


@csrf_exempt
def rename_proto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 500001, 'msg': '请登录'})
    proto_id = request.POST.get('proto_id')
    protos = Prototype.objects.filter(prototypeId=proto_id)
    if not protos.exists():
        return JsonResponse({'errno': 300001, 'msg': '设计原型不存在'})
    proto = protos.first()
    new_name = request.POST.get('new_name')
    proto.protoName = new_name
    proto.save()
    return JsonResponse({'errno': 0, 'msg': '修改成功'})
