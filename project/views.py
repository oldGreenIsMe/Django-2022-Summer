import os
import pdfkit
import datetime
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from team.models import *
from project.models import *


@csrf_exempt
def createProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    projName = request.POST.get('proj_name')
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    projTeam = Team.objects.get(teamid=request.POST.get('team_id'))
    if not UserTeam.objects.filter(user=user, team=projTeam).exists():
        return JsonResponse({'errno': 500001, 'msg': '没有权限创建项目'})
    projInfo = request.POST.get('proj_info')
    if projInfo is None or projInfo == "":
        projInfo = "暂无简介"
    startTime = request.POST.get('start_time')
    startTimeRecord = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M') + datetime.timedelta(hours=8)
    endTime = request.POST.get('end_time')
    projects = Project.objects.filter(projName=projName, projTeam=projTeam)
    if projects.exists():
        return JsonResponse({'errno': 400001, 'msg': '项目名称重复'})
    project = Project(projName=projName, projCreator=user, projTeam=projTeam, projInfo=projInfo, startTime=startTime,
                      endTime=endTime, deletePerson=None, deleteTime=None, startTimeRecord=startTimeRecord)
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
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    team = project.projTeam
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    photo = request.FILES.get('photo')
    if project.photo != 'projImg/default.png':
        projPhotoDelete(instance=project)
    project.photo = photo
    project.save()
    return JsonResponse({'errno': 0, 'msg': '图片修改成功', 'photo': project.photo.url})


@csrf_exempt
def modifyProjInfo(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    projId = request.POST.get('proj_id')
    projects = Project.objects.filter(projId=projId)
    if not projects.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    project = projects.first()
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    team = project.projTeam
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    projName = request.POST.get('proj_name')
    projInfo = request.POST.get('proj_info')
    if projInfo is None or projInfo == "":
        projInfo = "暂无简介"
    startTime = request.POST.get('start_time')
    startTimeRecord = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M') + datetime.timedelta(hours=8)
    endTime = request.POST.get('end_time')
    projects = Project.objects.filter(projName=projName, projTeam=project.projTeam)
    if projects.exists() and projects.first() != project:
        return JsonResponse({'errno': 400001, 'msg': '项目名称重复'})
    project.projName = projName
    project.projInfo = projInfo
    project.startTime = startTime
    project.endTime = endTime
    project.startTimeRecord = startTimeRecord
    project.save()
    return JsonResponse({'errno': 0, 'msg': '项目信息修改成功'})


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
    team = project.projTeam
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    project.status = 2
    project.deletePerson = user
    project.deleteTime = time
    project.deleteTimeRecord = timezone.now()
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
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    team = project.projTeam
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    project.delete()
    return JsonResponse({'errno': 0, 'msg': '项目删除成功'})


@csrf_exempt
def recoverProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    projid = request.POST.get('proj_id')
    projs = Project.objects.filter(projId=projid)
    if not projs.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
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
def detailProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    projid = request.POST.get('proj_id')
    projs = Project.objects.filter(projId=projid)
    if not projs.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    proj = projs.first()
    proj_name = proj.projName
    creator = proj.projCreator
    info = proj.projInfo
    start = proj.startTime
    end = proj.endTime
    team = proj.projTeam
    member_set = team.user_set.all()
    if not member_set.filter(userid=users.first().userid).exists():
        return JsonResponse({'errno': 500003, 'msg': '没有权限查看该项目'})
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
    return JsonResponse({'errno': 0, 'msg': '查看成功', 'proj_name': proj_name, 'proj_creator': creator.username,
                         'proj_start': start, 'proj_end': end, 'proj_team': team.teamname, 'proj_team_id': team.teamid,
                         'proj_info': info, 'members': members, 'proj_photo': proj.photo.url})


@csrf_exempt
def getDeletedProjList(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    teams = Team.objects.filter(teamid=request.POST.get('team_id'))
    if not teams.exists():
        return JsonResponse({'errno': 400005, 'msg': '团队不存在'})
    team = teams.first()
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500004, 'msg': '没有权限查看该信息'})
    projList = team.project_set.all().order_by('-deleteTimeRecord')
    data = []
    for proj in projList:
        if proj.deletePerson is None:
            continue
        data.append({
            'proj_id': int(proj.projId),
            'proj_name': proj.projName,
            'delete_time': proj.deleteTime,
            'delete_user_id': int(proj.deletePerson.userid),
            'delete_user_name': proj.deletePerson.username,
            'proj_info': proj.projInfo
        })
    return JsonResponse({'errno': 0, 'msg': '已删除项目查询成功', 'data': data})


@csrf_exempt
def copy_project(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    user = users.first()
    proj_id = request.POST.get('proj_id')
    projs = Project.objects.filter(projId=proj_id)
    if not projs.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    proj = projs.first()
    team = proj.projTeam
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    copy_num = proj.copy_num
    if Project.objects.filter(projName=proj.projName + '(' + str(copy_num + 1) + ')', projTeam=proj.projTeam).exists():
        return JsonResponse({'errno': 600001, 'msg': '复制时发现同名项目'})
    copy_time = request.POST.get('copy_time')
    copy_time_record = datetime.datetime.strptime(copy_time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    proj_copy = Project(projName=proj.projName + '(' + str(copy_num + 1) + ')', projCreator=user,
                        projTeam=proj.projTeam, projInfo=proj.projInfo, startTimeRecord=proj.startTimeRecord,
                        startTime=proj.startTime, endTime=proj.endTime, deletePerson=None, deleteTime=None)
    proj_copy.save()
    proj.copy_num = copy_num + 1
    proj.save()
    files = File.objects.filter(projectId=proj)
    for file in files:
        file_copy = File(fileName=file.fileName, fileCreator=user, content=file.content, create=copy_time,
                         lastEditTime=copy_time, lastEditUser=user, projectId=proj_copy, new=2,
                         lastEditTimeRecord=copy_time_record, fileTeam=file.fileTeam, fileFolder=file.fileFolder)
        file_copy.save()
    protos = Prototype.objects.filter(projectId=proj)
    for proto in protos:
        proto = Prototype(projectId=proj_copy, protoName=proto.protoName, protoCreator=user,
                          protoContent=proto.protoContent, protoPhoto=proto.protoPhoto, canvas_width=proto.canvas_width,
                          canvas_height=proto.canvas_height)
        proto.save()
    return JsonResponse({'errno': 0, 'msg': '复制成功'})


@csrf_exempt
def create_proto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    projid = request.POST.get('proj_id')
    projs = Project.objects.filter(projId=projid)
    if not projs.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    proj = projs.first()
    user = users.first()
    team = proj.projTeam
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    proto_name = request.POST.get('proto_name')
    canvas_height = request.POST.get('canvas_height', 500)
    canvas_width = request.POST.get('canvas_width', 500)
    proto_content = request.POST.get('proto_content', '[]')
    protos = Prototype.objects.filter(protoName=proto_name, projectId=proj)
    if protos.exists():
        return JsonResponse({'errno': 400010, 'msg': '设计原型名称重复'})
    proto = Prototype(projectId=proj, protoName=proto_name, protoCreator=users.first(), canvas_height=canvas_height,
                      canvas_width=canvas_width, protoContent=proto_content)
    proto.save()
    return JsonResponse({'errno': 0, 'msg': '创建成功', 'proto_id': proto.prototypeId})


@csrf_exempt
def upload_proto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    proto_id = request.POST.get('proto_id')
    protos = Prototype.objects.filter(prototypeId=proto_id)
    if not protos.exists():
        return JsonResponse({'errno': 300001, 'msg': '设计原型不存在'})
    proto = protos.first()
    proj = proto.projectId
    team = proj.projTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    proto_content = request.POST.get('proto_content')
    canvas_width = request.POST.get('canvas_width')
    canvas_height = request.POST.get('canvas_height')
    proto.protoContent = proto_content
    proto.canvas_width = canvas_width
    proto.canvas_height = canvas_height
    proto.save()
    return JsonResponse({'errno': 0, 'msg': '上传成功'})


@csrf_exempt
def get_proto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    proto_id = request.POST.get('proto_id')
    protos = Prototype.objects.filter(prototypeId=proto_id)
    if not protos.exists():
        return JsonResponse({'errno': 300001, 'msg': '设计原型不存在'})
    proto = protos.first()
    proj = proto.projectId
    team = proj.projTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500004, 'msg': '没有权限查看该信息'})
    proto_content = proto.protoContent
    canvas_width = proto.canvas_width
    canvas_height = proto.canvas_height
    return JsonResponse({'errno': 0, 'msg': '获取成功', 'proto_content': proto_content, 'canvas_width': canvas_width,
                         'canvas_height': canvas_height})


@csrf_exempt
def proj_proto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    proj_id = request.POST.get('proj_id')
    if not Project.objects.filter(projId=proj_id).exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    proj = Project.objects.filter(projId=proj_id).first()
    team = proj.projTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500004, 'msg': '没有权限查看该信息'})
    protos = Prototype.objects.filter(projectId=proj_id)
    protos_info = []
    for proto in protos:
        protos_info.append(
            {
                'proto_id': proto.prototypeId,
                'proto_name': proto.protoName,
                'proto_photo': proto.protoPhoto,
                'creator_id': proto.protoCreator.userid,
                'creator_name': proto.protoCreator.username,
                'creator_truename': proto.protoCreator.truename,
            }
        )
    return JsonResponse({'errno': 0, 'msg': '获取成功', 'protos_info': protos_info})


@csrf_exempt
def rename_proto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    proto_id = request.POST.get('proto_id')
    protos = Prototype.objects.filter(prototypeId=proto_id)
    if not protos.exists():
        return JsonResponse({'errno': 300001, 'msg': '设计原型不存在'})
    proto = protos.first()
    proj = proto.projectId
    team = proj.projTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    new_name = request.POST.get('new_name')
    projid = proto.projectId
    if Prototype.objects.filter(protoName=new_name, projectId=projid).exists():
        return JsonResponse({'errno': 400010, 'msg': '设计原型名称重复'})
    proto.protoName = new_name
    proto.save()
    return JsonResponse({'errno': 0, 'msg': '修改成功'})


@csrf_exempt
def delete_proto(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    proto_id = request.POST.get('proto_id')
    protos = Prototype.objects.filter(prototypeId=proto_id)
    if not protos.exists():
        return JsonResponse({'errno': 300001, 'msg': '设计原型不存在'})
    proto = protos.first()
    proj = proto.projectId
    team = proj.projTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    proto.delete()
    return JsonResponse({'errno': 0, 'msg': '删除成功'})


@csrf_exempt
def upload_proto_photo(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    proto_id = request.POST.get('proto_id')
    protos = Prototype.objects.filter(prototypeId=proto_id)
    if not protos.exists():
        return JsonResponse({'errno': 300001, 'msg': '设计原型不存在'})
    proto = protos.first()
    proj = proto.projectId
    team = proj.projTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500002, 'msg': '没有权限操作该项目'})
    photo = request.POST.get('base64_photo')
    proto.protoPhoto = photo
    proto.save()
    return JsonResponse({'errno': 0, 'msg': '上传成功'})


@csrf_exempt
def createFile(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    fileName = request.POST.get('file_name')
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    team = Team.objects.get(teamid=request.POST.get('teamid'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500005, 'msg': '没有权限创建文档'})
    createTime = request.POST.get('create_time')
    time = datetime.datetime.strptime(createTime, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    judge = int(request.POST.get('judge'))
    folderId = int(request.POST.get('folder_id'))
    model_content = ''
    model_id = int(request.POST.get('model'))
    if model_id != 0:
        model_content = FileModel.objects.filter(model_id=model_id).first().model_content
    if judge == 0:  # 建立项目文档
        projects = Project.objects.filter(projId=request.POST.get('proj_id'))
        if not projects.exists():
            return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
        project = projects.first()
        files = File.objects.filter(projectId=project.projId, fileName=fileName)
        if files.first() is not None:
            return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
        file = File(fileName=fileName, fileCreator=user, content=model_content, create=createTime,
                    lastEditTime=createTime, lastEditUser=user, lastEditTimeRecord=time, projectId=project, judge=0,
                    fileTeam=team, file_model=model_id, new=1)
        file.save()
    else:           # 建立团队文档
        if folderId == 0:
            folder = None
        else:
            folders = Folder.objects.filter(folderId=folderId)
            if not folders.exists():
                return JsonResponse({'errno': 700002, 'msg': '文件夹不存在'})
            folder = folders.first()
        files = File.objects.filter(fileTeam=team, judge=1, fileName=fileName, fileFolder=folder)
        if files.first() is not None:
            return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
        file = File(fileName=fileName, fileCreator=user, content=model_content, create=createTime,
                    lastEditTime=createTime, lastEditUser=user, lastEditTimeRecord=time, judge=1, fileTeam=team,
                    fileFolder=folder, file_model=model_id, new=1)
        file.save()
    return JsonResponse({'errno': 0, 'msg': '文档创建成功', 'file_id': file.fileId})


@csrf_exempt
def deleteFile(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    files = File.objects.filter(fileId=request.POST.get('file_id'))
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    proj = file.projectId
    team = proj.projTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500006, 'msg': '没有权限操作该文档'})
    file.delete()
    return JsonResponse({'errno': 0, 'msg': '文档删除成功'})


@csrf_exempt
def modifyFile(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    files = File.objects.filter(fileId=request.POST.get('file_id'))
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    team = file.fileTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500006, 'msg': '没有权限操作该文档'})
    content = request.POST.get('content')
    modifyTime = request.POST.get('modify_time')
    time = datetime.datetime.strptime(modifyTime, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    file.content = content
    file.lastEditTime = modifyTime
    file.lastEditUser = user
    file.lastEditTimeRecord = time
    file.save()
    return JsonResponse({'errno': 0, 'msg': '文档编辑成功'})


@csrf_exempt
def copy_project_file(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    file_id = request.POST.get('file_id')
    files = File.objects.filter(fileId=file_id)
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    copy_to_proj = request.POST.get('copy_to_proj')
    projs = Project.objects.filter(projId=copy_to_proj)
    if not projs.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    proj = projs.first()
    file = files.first()
    file_team = file.fileTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=file_team).exists():
        return JsonResponse({'errno': 500006, 'msg': '没有权限操作该文档'})
    if proj.projTeam.teamid != file_team.teamid:
        return JsonResponse({'errno': 500006, 'msg': '没有权限操作该文档'})
    copy_time = request.POST.get('copy_time')
    time = datetime.datetime.strptime(copy_time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))

    i = 1
    new_name = file.fileName + '(' + str(i) + ')'
    while File.objects.filter(projectId=proj.projId, fileName=new_name):
        i += 1
        new_name = file.fileName + '(' + str(i) + ')'
    copy_file = File(fileName=new_name, fileCreator=user, content=file.content, create=copy_time,
                     lastEditTime=copy_time, lastEditUser=user, lastEditTimeRecord=time, projectId=proj, judge=0,
                     fileTeam=file.fileTeam, new=2, file_model=file.file_model)
    copy_file.save()
    return JsonResponse({'errno': 0, 'msg': '复制项目文件成功'})


@csrf_exempt
def renameFile(request):
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    modifyTime = request.POST.get('modify_time')
    time = datetime.datetime.strptime(modifyTime, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    files = File.objects.filter(fileId=request.POST.get('file_id'))
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    judge = file.judge
    fileName = request.POST.get('file_name')
    if judge == 0:
        projects = Project.objects.filter(projId=request.POST.get('proj_id'))
        if not projects.exists():
            return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
        project = projects.first()
        team = project.projTeam
        if not UserTeam.objects.filter(user=user, team=team).exists():
            return JsonResponse({'errno': 500006, 'msg': '没有权限操作该文档'})
        files = File.objects.filter(projectId=project.projId, fileName=fileName, judge=0)
        if files.first() is not None:
            return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
    else:
        team = Team.objects.get(teamid=request.POST.get('teamid'))
        if not UserTeam.objects.filter(user=user, team=team).exists():
            return JsonResponse({'errno': 500006, 'msg': '没有权限操作该文档'})
        files = File.objects.filter(fileTeam=team, fileName=fileName, judge=1, fileFolder=file.fileFolder)
        if files.first() is not None:
            return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
    file.fileName = fileName
    file.lastEditTime = modifyTime
    file.lastEditUser = user
    file.lastEditTimeRecord = time
    file.save()
    return JsonResponse({'errno': 0, 'msg': '文档重命名成功'})


@csrf_exempt
def getFileList(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    projects = Project.objects.filter(projId=request.POST.get('proj_id'))
    if not projects.exists():
        return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
    project = projects.first()
    team = project.projTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500004, 'msg': '没有权限查看该信息'})
    fileList = project.file_set.all().order_by('-lastEditTimeRecord')
    data = []
    for file in fileList:
        data.append({
            'file_id': int(file.fileId),
            'file_name': file.fileName,
            'file_creator': User.objects.filter(userid=file.fileCreator.userid).first().username,
            'create_time': file.create,
            'last_modify_time': file.lastEditTime,
            'last_modify_user_id': int(file.lastEditUser.userid),
            'last_modify_user_name': file.lastEditUser.username
        })
    return JsonResponse({'errno': 0, 'msg': '文档列表查询成功', 'data': data})


@csrf_exempt
def getFileContent(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    files = File.objects.filter(fileId=request.POST.get('file_id'))
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    team = file.fileTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500004, 'msg': '没有权限查看该信息'})
    return JsonResponse({'errno': 0, 'msg': '文档内容获取成功', 'content': file.content})


@csrf_exempt
def upload_file_image(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    files = File.objects.filter(fileId=request.POST.get('file_id'))
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    team = file.fileTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500004, 'msg': '没有权限查看该信息'})
    image = request.FILES.get('image')
    file_image = FileImage(file=file, image=image)
    file_image.save()
    return JsonResponse({'errno': 0, 'msg': '上传图片成功', 'url': file_image.image.url})


@csrf_exempt
def edit_file(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    fileid = request.POST.get('fileid')
    files = File.objects.filter(fileId=fileid)
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    team = file.fileTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500004, 'msg': '没有权限查看该信息'})
    model_id = file.file_model
    model = ''
    if model_id != 0:
        model = FileModel.objects.filter(model_id=model_id).first().model_content
    if file.new == 1 or file.new == 2:
        new = file.new
        file.new = 0
        file.save()
        return JsonResponse({'errno': 0, 'msg': '获取文档状态成功', 'new': new, 'model': model})
    else:
        return JsonResponse({'errno': 0, 'msg': '获取文档状态成功', 'new': file.new, 'model': model})


@csrf_exempt
def search_user_project(request):
    if request.method == 'POST':
        user = User.objects.get(userid=request.META.get('HTTP_USERID'))
        projName = request.POST.get('projName')
        teams = user.team_belonged.all()
        data = []
        for team in teams:
            projects = Project.objects.filter(projTeam=team, status=1, projName__icontains=projName)
            for project in projects:
                data.append({
                    'projName': project.projName,
                    'projId': project.projId,
                    'photo': project.photo.url
                })
        return JsonResponse({'errno': 0, 'data': data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def search_team_project(request):
    if request.method == 'POST':
        projName = request.POST.get('projName')
        team = Team.objects.get(teamid=request.POST.get('teamid'))
        user = User.objects.get(userid=request.META.get('HTTP_USERID'))
        if not UserTeam.objects.filter(user=user, team=team).exists():
            return JsonResponse({'errno': 500004, 'msg': '没有权限查看该信息'})
        projects = Project.objects.filter(projTeam=team, status=1, projName__icontains=projName)
        data = []
        for project in projects:
            data.append({
                'projName': project.projName,
                'projId': project.projId,
                'photo': project.photo.url
            })
        return JsonResponse({'errno': 0, 'data': data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def project_order(request):
    if request.method == 'POST':
        according = request.POST.get('according')
        team = Team.objects.get(teamid=request.POST.get('teamid'))
        user = User.objects.get(userid=request.META.get('HTTP_USERID'))
        if not UserTeam.objects.filter(user=user, team=team).exists():
            return JsonResponse({'errno': 500010, 'msg': '没有权限进行该操作'})
        projects = []
        if according == '创建时间从早到晚':
            projects = team.project_set.filter(status=1).order_by('projId')
        elif according == '创建时间从晚到早':
            projects = team.project_set.filter(status=1).order_by('-projId')
        elif according == '名称字典序正序':
            projects = team.project_set.filter(status=1).order_by('projName')
        elif according == '名称字典序倒序':
            projects = team.project_set.filter(status=1).order_by('-projName')
        elif according == '开始时间从早到晚':
            projects = team.project_set.filter(status=1).order_by('startTimeRecord')
        elif according == '开始时间从晚到早':
            projects = team.project_set.filter(status=1).order_by('-startTimeRecord')
        data = []
        for project in projects:
            data.append({
                'projId': project.projId,
                'projName': project.projName,
                'startTime': project.startTime,
                'photo': project.photo.url
            })
        return JsonResponse({'errno': 0, 'data': data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def get_pdf(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    file_id = request.POST.get('file_id')
    files = File.objects.filter(fileId=file_id)
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    team = file.fileTeam
    file_name = request.POST.get('file_name')
    html_str = '<html>\n' + \
               '    <head>\n' + \
               '    <meta charset="utf-8">\n' + \
               '<title>Markdoc Preview</title>\n' + \
               '    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n' + \
               '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + \
               '    <style type="text/css">html {font-family: sans-serif; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; }body {margin: 0;}article,aside,details,figcaption,figure,footer,header,hgroup,main,nav,section,summary {display: block;}audio,canvas,progress,video {display: inline-block; vertical-align: baseline; }audio:not([controls]) {display: none;height: 0;}[hidden],template {display: none;}a {background: transparent;}a:active,a:hover {outline: 0;}abbr[title] {border-bottom: 1px dotted;}b,strong {font-weight: bold;}dfn {font-style: italic;}h1 {font-size: 2em;margin: 0.67em 0;}mark {background: #ff0;color: #000;}small {font-size: 80%;}sub,sup {font-size: 75%;line-height: 0;position: relative;vertical-align: baseline;}sup {top: -0.5em;}sub {bottom: -0.25em;}img {border: 0;}svg:not(:root) {overflow: hidden;}figure {margin: 1em 40px;}hr {-moz-box-sizing: content-box;box-sizing: content-box;height: 0;}pre {overflow: auto;}code,kbd,pre,samp {font-family: monospace, monospace;font-size: 1em;}button,input,optgroup,select,textarea {color: inherit; font: inherit; margin: 0; }button {overflow: visible;}button,select {text-transform: none;}button,html input[type="button"], input[type="reset"],input[type="submit"] {-webkit-appearance: button; cursor: pointer; }button[disabled],html input[disabled] {cursor: default;}button::-moz-focus-inner,input::-moz-focus-inner {border: 0;padding: 0;}input {line-height: normal;}input[type="checkbox"],input[type="radio"] {box-sizing: border-box; padding: 0; }input[type="number"]::-webkit-inner-spin-button,input[type="number"]::-webkit-outer-spin-button {height: auto;}input[type="search"] {-webkit-appearance: textfield; -moz-box-sizing: content-box;-webkit-box-sizing: content-box; box-sizing: content-box;}input[type="search"]::-webkit-search-cancel-button,input[type="search"]::-webkit-search-decoration {-webkit-appearance: none;}fieldset {border: 1px solid #c0c0c0;margin: 0 2px;padding: 0.35em 0.625em 0.75em;}legend {border: 0; padding: 0; }textarea {overflow: auto;}optgroup {font-weight: bold;}table {border-collapse: collapse;border-spacing: 0;}td,th {padding: 0;}* {-webkit-box-sizing: border-box;-moz-box-sizing: border-box;box-sizing: border-box;}*:before,*:after {-webkit-box-sizing: border-box;-moz-box-sizing: border-box;box-sizing: border-box;}html {font-size: 62.5%;-webkit-tap-highlight-color: rgba(0, 0, 0, 0);}body {font-family: \'Helvetica Neue\', Helvetica, Arial, \'Microsoft Yahei\', sans-serif;font-size: 14px;line-height: 1.42857143;color: #333333;background-color: #ffffff;}input,button,select,textarea {font-family: inherit;font-size: inherit;line-height: inherit;}a {color: #428bca;text-decoration: none;}a:hover,a:focus {color: #2a6496;text-decoration: underline;}a:focus {outline: thin dotted;outline: 5px auto -webkit-focus-ring-color;outline-offset: -2px;}figure {margin: 0;}img {vertical-align: middle;}.hljs {display: block;overflow-x: auto;padding: 0.5em;background: #f0f0f0;-webkit-text-size-adjust: none;}.hljs,.hljs-subst,.hljs-tag .hljs-title,.nginx .hljs-title {color: black;}.hljs-string,.hljs-title,.hljs-constant,.hljs-parent,.hljs-tag .hljs-value,.hljs-rules .hljs-value,.hljs-preprocessor,.hljs-pragma,.haml .hljs-symbol,.ruby .hljs-symbol,.ruby .hljs-symbol .hljs-string,.hljs-template_tag,.django .hljs-variable,.smalltalk .hljs-class,.hljs-addition,.hljs-flow,.hljs-stream,.bash .hljs-variable,.apache .hljs-tag,.apache .hljs-cbracket,.tex .hljs-command,.tex .hljs-special,.erlang_repl .hljs-function_or_atom,.asciidoc .hljs-header,.markdown .hljs-header,.coffeescript .hljs-attribute {color: #800;}.smartquote,.hljs-comment,.hljs-annotation,.diff .hljs-header,.hljs-chunk,.asciidoc .hljs-blockquote,.markdown .hljs-blockquote {color: #888;}.hljs-number,.hljs-date,.hljs-regexp,.hljs-literal,.hljs-hexcolor,.smalltalk .hljs-symbol,.smalltalk .hljs-char,.go .hljs-constant,.hljs-change,.lasso .hljs-variable,.makefile .hljs-variable,.asciidoc .hljs-bullet,.markdown .hljs-bullet,.asciidoc .hljs-link_url,.markdown .hljs-link_url {color: #080;}.hljs-label,.hljs-javadoc,.ruby .hljs-string,.hljs-decorator,.hljs-filter .hljs-argument,.hljs-localvars,.hljs-array,.hljs-attr_selector,.hljs-important,.hljs-pseudo,.hljs-pi,.haml .hljs-bullet,.hljs-doctype,.hljs-deletion,.hljs-envvar,.hljs-shebang,.apache .hljs-sqbracket,.nginx .hljs-built_in,.tex .hljs-formula,.erlang_repl .hljs-reserved,.hljs-prompt,.asciidoc .hljs-link_label,.markdown .hljs-link_label,.vhdl .hljs-attribute,.clojure .hljs-attribute,.asciidoc .hljs-attribute,.lasso .hljs-attribute,.coffeescript .hljs-property,.hljs-phony {color: #88f;}.hljs-keyword,.hljs-id,.hljs-title,.hljs-built_in,.css .hljs-tag,.hljs-javadoctag,.hljs-phpdoc,.hljs-dartdoc,.hljs-yardoctag,.smalltalk .hljs-class,.hljs-winutils,.bash .hljs-variable,.apache .hljs-tag,.hljs-type,.hljs-typename,.tex .hljs-command,.asciidoc .hljs-strong,.markdown .hljs-strong,.hljs-request,.hljs-status {font-weight: bold;}.asciidoc .hljs-emphasis,.markdown .hljs-emphasis {font-style: italic;}.nginx .hljs-built_in {font-weight: normal;}.coffeescript .javascript,.javascript .xml,.lasso .markup,.tex .hljs-formula,.xml .javascript,.xml .vbscript,.xml .css,.xml .hljs-cdata {opacity: 0.5;}#container {padding: 15px;margin-left:20px;}pre {border: 1px solid #ccc;border-radius: 4px;display: block;}pre code {white-space: pre-wrap;}.hljs,code {font-family: Monaco, Menlo, Consolas, \'Courier New\', monospace;}pre{background-color: #dddddd;padding:8px 0px 8px 30px;word-wrap: break-word;}table tbody tr:nth-child(2n) {background: rgba(158,188,226,0.12); }:not(pre) > code {padding: 2px 4px;font-size: 90%;color: #c7254e;background-color: #f9f2f4;white-space: nowrap;border-radius: 4px;}th, td {border: 1px solid #ccc;padding: 6px 12px;}blockquote {border-left-width: 10px;background-color: rgba(102,128,153,0.05);border-top-right-radius: 5px;border-bottom-right-radius: 5px;padding: 1px 20px}blockquote.pull-right small:before,blockquote.pull-right .small:before {content: \'\'}blockquote.pull-right small:after,blockquote.pull-right .small:after {content: \'\\00A0 \\2014\'}blockquote:before,blockquote:after {content: ""}blockquote {margin: 0 0 1.1em}blockquote p {margin-bottom: 1.1em;font-size: 1em;line-height: 1.45}blockquote ul:last-child,blockquote ol:last-child {margin-bottom: 0}blockquote {margin: 0 0 21px;border-left: 10px solid #dddddd;}\n' + \
               '    </style>\n' + \
               '    </head>\n' + \
               '    <body marginwidth="0" marginheight="0">\n' + \
               '    <script>document.body.style.zoom = 1.5</script>\n' + \
               '        <div id="container" style="margin-left:11.5%;margin-right:11.5%;">' + \
               file.content + '</div>\n' + \
               '</body>\n' + \
               '</html>'
    file_dir = settings.MEDIA_ROOT + '/filePDF/'
    pdfkit.from_string(html_str, file_dir + file_name)
    file_response = FileResponse(open("media/filePDF/{name}".format(name=file_name), 'rb'), as_attachment=True,
                                 filename=file.fileName + '.pdf')
    return file_response


@csrf_exempt
def delete_pdf(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    file_name = request.POST.get('file_name')
    os.remove('media/filePDF/' + file_name)
    return JsonResponse({'errno': 0, 'msg': '删除服务器文件成功'})


@csrf_exempt
def open_proto_preview(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    project = Project.objects.get(projId=request.POST.get('proj_id'))
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    team = project.projTeam
    user_teams = UserTeam.objects.filter(user=user, team=team)
    if not user_teams.exists():
        return JsonResponse({'errno': 300014, 'msg': '当前用户非团队成员，无权限'})
    if project.preview_status != 2:
        project.preview_status = 2
    project.save()
    return JsonResponse({'errno': 0, 'msg': '打开项目原型预览成功'})


@csrf_exempt
def close_proto_preview(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    project = Project.objects.get(projId=request.POST.get('proj_id'))
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    team = project.projTeam
    user_teams = UserTeam.objects.filter(user=user, team=team)
    if not user_teams.exists():
        return JsonResponse({'errno': 300014, 'msg': '当前用户非团队成员，无权限'})
    if project.preview_status == 2:
        project.preview_status = 1
    elif project.preview_status == 1:
        return JsonResponse({'errno': 300015, 'msg': '项目原型预览已关闭'})
    else:
        return JsonResponse({'errno': 300016, 'msg': '项目原型预览尚未创建'})
    project.save()
    return JsonResponse({'errno': 0, 'msg': '关闭项目原型预览成功'})


@csrf_exempt
def view_proto_preview(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    project = Project.objects.get(projId=request.POST.get('proj_id'))
    if project.preview_status == 0:
        return JsonResponse({'errno': 300017, 'msg': '项目原型预览不存在'})
    elif project.preview_status == 1:
        return JsonResponse({'errno': 300018, 'msg': '项目原型预览已关闭'})
    proto_data = []
    protos = Prototype.objects.filter(projectId=project)
    for proto in protos:
        proto_data.append({
            'proto_id': proto.prototypeId,
            'proto_name': proto.protoName,
            'canvas_width': proto.canvas_width,
            'canvas_height': proto.canvas_height,
            'protos_content': proto.protoContent
        })
    return JsonResponse({'errno': 0, 'all_proto_content': proto_data})


@csrf_exempt
def view_preview_status(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    project = Project.objects.get(projId=request.POST.get('proj_id'))
    return JsonResponse({'errno': 0, 'preview_status': project.preview_status})
