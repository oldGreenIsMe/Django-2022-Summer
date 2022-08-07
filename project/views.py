from django.utils import timezone
from django.core import serializers
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from project.models import *
from team.models import *
import datetime


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
    startTimeRecord = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M')
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
    photo = request.FILES.get('photo')
    if project.photo != 'projImg/default.png':
        projPhotoDelete(instance=project)
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
    projName = request.POST.get('proj_name')
    projInfo = request.POST.get('proj_info')
    if projInfo is None or projInfo == "":
        projInfo = "暂无简介"
    startTime = request.POST.get('start_time')
    startTimeRecord = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M')
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
    copy_num = proj.copy_num
    if Project.objects.filter(projName=proj.projName + '(' + str(copy_num + 1) + ')', projTeam=proj.projTeam).exists():
        return JsonResponse({'errno': 600001, 'msg': '复制时发现同名项目'})
    copy_time = request.POST.get('copy_time')
    proj_copy = Project(projName=proj.projName + '(' + str(copy_num + 1) + ')', projCreator=user,
                        projTeam=proj.projTeam, projInfo=proj.projInfo,
                        startTime=proj.startTime, endTime=proj.endTime, deletePerson=None, deleteTime=None)
    proj_copy.save()
    proj.copy_num = copy_num + 1
    proj.save()
    files = File.objects.filter(projectId=proj)
    for file in files:
        file_copy = File(fileName=file.fileName, fileCreator=user, content=file.content, create=copy_time,
                         lastEditTime=copy_time, lastEditUser=user, projectId=proj_copy, new=2)
        file_copy.save()
    protos = Prototype.objects.filter(projectId=proj)
    for proto in protos:
        proto = Prototype(projectId=proj_copy, protoName=proto.protoName, protoCreator=user)
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
    proto_name = request.POST.get('proto_name')
    protos = Prototype.objects.filter(protoName=proto_name, projectId=projid)
    if protos.exists():
        return JsonResponse({'errno': 400010, 'msg': '设计原型名称重复'})
    proto = Prototype(projectId=proj, protoName=proto_name, protoCreator=users.first())
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
    proto_content = request.POST.get('proto_content')
    canvas_width = request.POST.get('canvas_width')
    canvas_height = request.POST.get('canvas_height')
    proto = protos.first()
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
    new_name = request.POST.get('new_name')
    proto = protos.first()
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
    createTime = request.POST.get('create_time')
    judge = request.POST.get('judge')
    if judge == 0:  # 建立项目文档
        projects = Project.objects.filter(projId=request.POST.get('proj_id'))
        if not projects.exists():
            return JsonResponse({'errno': 400002, 'msg': '项目不存在'})
        project = projects.first()
        files = File.objects.filter(projectId=project.projId, fileName=fileName)
        if files.first() is not None:
            return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
        file = File(fileName=fileName, fileCreator=user, content="", create=createTime, lastEditTime=createTime,
                    lastEditUser=user, projectId=project, judge=0, fileTeam=team)
        file.save()
    else:  # 建立团队文档
        files = File.objects.filter(fileTeam=team, judge=1, fileName=fileName)
        if files.first() is not None:
            return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
        file = File(fileName=fileName, fileCreator=user, content="", create=createTime, lastEditTime=createTime,
                    lastEditUser=user, judge=1, fileTeam=team)
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
    content = request.POST.get('content')
    modifyTime = request.POST.get('modify_time')
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    file.content = content
    file.lastEditTime = modifyTime
    file.lastEditUser = user
    file.save()
    return JsonResponse({'errno': 0, 'msg': '文档编辑成功'})


@csrf_exempt
def renameFile(request):
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
        files = File.objects.filter(projectId=project.projId, fileName=fileName, judge=0)
        if files.first() is not None:
            return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
    else:
        team = Team.objects.get(teamid=request.POST.get('teamid'))
        files = File.objects.filter(fileTeam=team, fileName=fileName, judge=1)
        if files.first() is not None:
            return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
    file.fileName = fileName
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
    return JsonResponse({'errno': 0, 'msg': '文档内容获取成功', 'content': file.content})


@csrf_exempt
def upload_file_image(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    files = File.objects.filter(fileId=request.POST.get('file_id'))
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    image = request.FILES.get('image')
    file_image = FileImage(file=files.first(), image=image)
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
    if file.new == 1:
        file.new = 0
        file.save()
        return JsonResponse({'errno': 0, 'msg': '获取文档状态成功', 'new': 1})
    else:
        return JsonResponse({'errno': 0, 'msg': '获取文档状态成功', 'new': 0})


@csrf_exempt
def file_center(request):
    if request.method == 'POST':
        request.META.get('HTTP_USREID')
        teamid = request.POST.get('teamid')
        team = Team.objects.get(teamid=teamid)
        team_files = File.object.filter(fileTeam=team, judge=1)
        team_data = []
        for team_file in team_files:
            team_data.append({
                'fileId': team_file.fileId,
                'fileName': team_file.fileName
            })
        projects = Project.objects.filter(projTeam=team)
        projects_data = []
        for project in projects:
            files_data = []
            files = File.objects.filter(projectId=project, judge=0)
            for file in files:
                files_data.append({
                    'fileId': file.fileId,
                    'fileName': file.fileName
                })
            projects_data.append({
                'projectId': project.projId,
                'projName': project.projName,
                'files_data': files_data
            })
        return JsonResponse({'errno': 0, 'data': projects_data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


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
                    'photo': project.photo
                })
        return JsonResponse({'errno': 0, 'data': data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def search_team_project(request):
    if request.method == 'POST':
        user = User.objects.get(userid=request.META.get('HTTP_USERID'))
        projName = request.POST.get('projName')
        team = Team.objects.get(teamid=request.POST.get('teamid'))
        projects = Project.objects.filter(projTeam=team, status=1, projName__icontains=projName)
        data = []
        for project in projects:
            data.append({
                'projName': project.projName,
                'projId': project.projId,
                'photo': project.photo
            })
        return JsonResponse({'errno': 0, 'data': data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def project_order(request):
    if request.method == 'POST':
        according = request.POST.get('according')
        team = Team.objects.filter(teamid=request.POST.get('teamid'))
        if according == '创建时间从早到晚':
            projects = Project.objects.filter(projTeam=team, status=1).order_by('projId')
        elif according == '创建时间从晚到早':
            projects = Project.objects.filter(projTeam=team, status=1).order_by('-projId')
        elif according == '名称字典序正序':
            projects = Project.objects.filter(projTeam=team, status=1).order_by('projName')
        elif according == '名称字典序倒序':
            projects = Project.objects.filter(projTeam=team, status=1).order_by('-projName')
        elif according == '开始时间从早到晚':
            projects = Project.objects.filter(projTeam=team, status=1).order_by('startTimeRecord')
        elif according == '开始时间从晚到早':
            projects = Project.objects.filter(projTeam=team, status=1).order_by('-startTimeRecord')
        data = []
        for project in projects:
            data.append({
                'projId': project.projId,
                'projName': project.projName,
                'startTime': project.startTime,
                'photo': project.photo
            })
        return JsonResponse({'errno': 0, 'data': data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})