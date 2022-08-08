import datetime
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from team.models import *
from utils.email import *
from project.models import *
from utils.token import create_token


@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        truename = request.POST.get('truename')
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        email = request.POST.get('email')
        if password_1 != password_2:
            return JsonResponse({'errno': 300002, 'msg': '两次输入的密码不一致'})
        if username == '' or truename == '':
            return JsonResponse({'errno': 300001, 'msg': '昵称与真实姓名不能为空'})
        user = User.objects.create(username=username, password=password_1, truename=truename, email=email)
        return JsonResponse({'errno': 0, 'msg': '注册成功', 'userid': user.userid})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        if userid.isdigit():
            users = User.objects.filter(userid=int(userid))
        else:
            users = User.objects.filter(email=userid)
        if users.exists():
            user = users.first()
            if user.password == password:
                token = create_token(str(user.userid))
                return JsonResponse({
                    'errno': 0,
                    'msg': '登录成功',
                    'data': {
                        'username': user.username,
                        'authorization': token,
                        'userid': user.userid,
                        'photo': user.photo.url,
                        'email': user.email,
                        'truename': user.truename
                    }
                })
            else:
                return JsonResponse({'errno': 100003, 'msg': '密码错误'})
        else:
            return JsonResponse({'errno': 100004, 'msg': '用户不存在'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def authorize_admin(request):
    if request.method == 'POST':
        teamid = request.POST.get('teamid')
        userid = request.POST.get('userid')
        creatorid = request.META.get('HTTP_USERID')
        creator = User.objects.get(userid=creatorid)
        team = Team.objects.get(teamid=teamid)
        user = User.objects.get(userid=userid)
        creator_team = UserTeam.objects.get(user=creator, team=team)
        if creator_team.permission != 2:
            return JsonResponse({'errno': 300003, 'msg': '当前用户并非创建者，无法添加管理员'})
        user_team = UserTeam.objects.get(user=user, team=team)
        if user_team.permission == 0:
            user_team.permission = 1
            user_team.save()
        return JsonResponse({'errno': 0, 'msg': '管理员授权成功'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def create_team(request):
    if request.method == 'POST':
        teamname = request.POST.get('teamname')
        creatorid = request.META.get('HTTP_USERID')
        creator = User.objects.get(userid=creatorid)
        team = Team.objects.create(teamname=teamname)
        UserTeam.objects.create(user=creator, team=team, permission=2)
        return JsonResponse({'errno': 0, 'msg': '创建团队成功', 'teamid': team.teamid})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def invite_user(request):
    adminid = request.META.get('HTTP_USERID')
    admin = User.objects.get(userid=adminid)
    teamid = request.POST.get('teamid')
    team = Team.objects.get(teamid=teamid)
    admin_team = UserTeam.objects.get(user=admin, team=team)
    if admin_team.permission == 0:
        return JsonResponse({'errno': 300004, 'msg': '非管理员，没有操作权限'})
    userid = request.POST.get('userid')
    if userid.isdigit():
        users = User.objects.filter(userid=int(userid))
    else:
        users = User.objects.filter(email=userid)
    if not users.exists():
        return JsonResponse({'errno': 300008, 'msg': '被邀请用户不存在'})
    user = users.first()
    if UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 300013, 'msg': '被邀请用户已在团队中'})
    if InviteMessage.objects.filter(user=user, team=team, status=1).exists():
        return JsonResponse({'errno': 300012, 'msg': '邀请或申请已存在'})
    InviteMessage.objects.create(team=team, user=user, inviter=admin, timeOrder=timezone.now())
    inviteMemberSendMethod(admin.username, user.username, user.userid, team.teamname, team.teamid, user.email)
    return JsonResponse({'errno': 0, 'msg': '用户邀请已发送'})


@csrf_exempt
def delete_member(request):
    if request.method == 'POST':
        adminid = request.META.get('HTTP_USERID')
        teamid = request.POST.get('teamid')
        admin = User.objects.get(userid=adminid)
        team = Team.objects.get(teamid=teamid)
        admin_team = UserTeam.objects.get(user=admin, team=team)
        if admin_team.permission == 0:
            return JsonResponse({'errno': 300004, 'msg': '非管理员，没有操作权限'})
        userid = request.POST.get('userid')
        user = User.objects.get(userid=userid)
        user_team = UserTeam.objects.get(user=user, team=team)
        if user_team.permission == 0:
            user.team_belonged.remove(team)
        else:
            return JsonResponse({'errno': 300005, 'msg': '被删用户是管理员，无法被删除'})
        return JsonResponse({'errno': 0, 'msg': '删除成员成功'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def userspace(request):
    userid = request.META.get('HTTP_USERID')
    user = User.objects.get(userid=userid)
    teams = user.team_belonged.all()
    data = []
    for team in teams:
        projs = team.project_set.filter(status=1)
        projs_data = []
        for proj in projs:
            projs_data.append({'proj_id': proj.projId, 'proj_name': proj.projName})
        data.append({
            'teamname': team.teamname,
            'teamid': team.teamid,
            'proj': projs_data
        })
    return JsonResponse({
        'data': data,
        'errno': 0
    })


@csrf_exempt
def teamspace(request):
    userid = request.META.get('HTTP_USERID')
    user = User.objects.get(userid=userid)
    teamid = request.POST.get('teamid')
    team = Team.objects.get(teamid=teamid)
    user_teams = UserTeam.objects.filter(user=user, team=team)
    if not user_teams.exists():
        return JsonResponse({'errno': 300006, 'msg': '您尚未加入该团队'})
    user_team = user_teams.first()
    projs = team.project_set.filter(status=1)
    # 将项目信息放入projdata
    projdata = []
    for proj in projs:
        projdata.append({
            'proj_id': proj.projId,
            'proj_name': proj.projName,
            'proj_photo': proj.photo.url,
            'proj_info': proj.projInfo
        })
    members = team.user_set.all()
    memberdata = []
    for member in members:
        member_team = UserTeam.objects.get(user=member, team=team)
        memberdata.append({
            'member_id': member.userid,
            'member_name': member.username,
            'member_photo': member.photo.url,
            'member_permission': member_team.permission
        })
    return JsonResponse({'projs': projdata, 'members': memberdata, 'permission': user_team.permission,
                         'teamname': team.teamname, 'errno': 0})


@csrf_exempt
def team_manage(request):
    teamid = request.POST.get('teamid')
    team = Team.objects.get(teamid=teamid)
    userid = request.META.get('HTTP_USERID')
    user = User.objects.get(userid=userid)
    user_team = UserTeam.objects.get(user=user, team=team)
    members = team.user_set.all()
    memberdata = []
    for member in members:
        member_team = UserTeam.objects.get(user=member, team=team)
        memberdata.append({
            'member_id': member.userid,
            'member_name': member.username,
            'member_photo': member.photo.url,
            'member_truename': member.truename,
            'member_email': member.email,
            'member_permission': member_team.permission
        })
    return JsonResponse({
        'permission': user_team.permission,
        'members': memberdata,
        'errno': 0
    })


@csrf_exempt
def modify_username(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 50001, 'msg': '用户尚未登录或注册'})
    user = users.first()
    username = request.POST.get('username')
    if username is None or username == '':
        return JsonResponse({'errno': 400001, 'msg': '没有做出修改'})
    user.username = username
    user.save()
    return JsonResponse({'errno': 0, 'msg': '名称修改成功', 'username': username})


@csrf_exempt
def modify_photo(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 500001, 'msg': '用户尚未登录或注册'})
    user = users.first()
    photo = request.FILES.get('photo', None)
    if photo is None:
        return JsonResponse({'errno': 400001, 'msg': '没有做出修改'})
    if user.photo != 'img/default_photo.png':
        userPhotoDelete(user)
    user.photo = photo
    user.save()
    return JsonResponse({'errno': 0, 'msg': '图片修改成功', 'photo': user.photo.url})


@csrf_exempt
def modify_password(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 100004, 'msg': '用户不存在'})
    user = users.first()
    password_1 = request.POST.get('password_1')
    password_2 = request.POST.get('password_2')
    if password_1 != password_2:
        return JsonResponse({'errno': 300002, 'msg': '两次输入的密码不一致'})
    user.password = password_1
    user.save()
    return JsonResponse({'errno': 0, 'msg': '修改密码成功'})


@csrf_exempt
def delete_team(request):
    if request.method == 'POST':
        userid = request.META.get('HTTP_USERID')
        teamid = request.POST.get('teamid')
        user = User.objects.get(userid=userid)
        team = Team.objects.get(teamid=teamid)
        user_team = UserTeam.objects.get(user=user, team=team)
        if user_team.permission != 2:
            return JsonResponse({'errno': 300010, 'msg': '非创造者，无权限删除队伍'})
        team.delete()
        return JsonResponse({'errno': 0, 'msg': '删除团队成功'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def handleInvitation(request):
    if request.method == 'POST':
        inviteId = request.POST.get('inviteId')
        inviteMessage = InviteMessage.objects.get(inviteId=inviteId)
        user = inviteMessage.user
        team = inviteMessage.team
        type = int(request.POST.get('type'))
        if type == 1 and not UserTeam.objects.filter(user=user, team=team).exists():
            UserTeam.objects.create(user=user, team=team, permission=0)
        nowTime = timezone.now()
        if inviteMessage.type == 2:
            invitationList = InviteMessage.objects.filter(user=user, team=team, type=2, status=1)
            for invitation in invitationList:
                invitation.timeOrder = nowTime
                invitation.status = type + 1
                invitation.save()
        inviteMessage.timeOrder = nowTime
        inviteMessage.status = type + 1
        inviteMessage.save()
        return JsonResponse({'errno': 0, 'msg': '请求处理成功'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def search_team(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        teams = Team.objects.filter(teamname__icontains=name)
        team_data = []
        for team in teams:
            team_data.append({
                'teamname': team.teamname,
                'teamid': team.teamid
            })
        return JsonResponse({'errno': 0, 'team_data': team_data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def apply_join(request):
    if request.method == 'POST':
        teamid = request.POST.get('teamid')
        team = Team.objects.get(teamid=teamid)
        userid = request.META.get('HTTP_USERID')
        user = User.objects.get(userid=userid)
        if InviteMessage.objects.filter(user=user, team=team, status=1).filter(Q(type=1) | Q(type=2)).exists():
            return JsonResponse({'errno': 300012, 'msg': '邀请或申请已存在'})
        userTeamList = UserTeam.objects.filter(team=team).filter(Q(permission=1) | Q(permission=2))
        nowTime = timezone.now()
        for userTeam in userTeamList:
            applyJoinMethod(userTeam.user.username, user.username, user.userid, team.teamname, team.teamid,
                            userTeam.user.email)
            InviteMessage.objects.create(team=team, inviter=userTeam.user, user=user, timeOrder=nowTime, type=2)
        return JsonResponse({'errno': 0, 'msg': '申请已发送'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def search_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        users = User.objects.filter(username__icontains=name)
        user_data = []
        for user in users:
            user_data.append({
                'username': user.teamname,
                'teamid': user.teamid,
                'photo': user.photo.url,
                'truename': user.truename,
                'email': user.email
            })
        return JsonResponse({'errno': 0, 'user_data': user_data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def sendVerifyCode(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    email = request.POST.get('email')
    users = User.objects.filter(email=email)
    if users.exists():
        return JsonResponse({'errno': 300007, 'msg': '邮箱已注册'})
    judge = int(request.POST.get('judge'))
    returnVal = sendVerifyCodeMethod(email, judge)
    return JsonResponse({'errno': 0, 'msg': '验证码发送成功', 'code': returnVal})


@csrf_exempt
def acceptInvitation(request):
    token = request.GET.get('token')
    data = inviteMemberCheck(token)
    teamId = data['teamid']
    userId = data['userid']
    judge = data['judge']
    team = Team.objects.get(teamid=teamId)
    user = User.objects.get(userid=userId)
    if not UserTeam.objects.filter(user=user, team=team).exists():
        UserTeam.objects.create(user=user, team=team, permission=0)
    else:
        if judge == 1:
            return render(request, 'jumpPage1.html')
        else:
            return render(request, 'jumpPage2.html')
    nowTime = timezone.now()
    if judge == 1:
        invitation = InviteMessage.objects.get(user=user, team=team, type=1, status=1)
        invitation.timeOrder = nowTime
        invitation.status = 2
        invitation.save()
        return render(request, 'jumpPage1.html')
    else:
        invitationList = InviteMessage.objects.filter(user=user, team=team, type=2, status=1)
        for invitation in invitationList:
            invitation.timeOrder = nowTime
            invitation.status = 2
            invitation.save()
        return render(request, 'jumpPage2.html')


@csrf_exempt
def createFolder(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    team = Team.objects.get(teamid=request.POST.get('team_id'))
    isRoot = request.POST.get('is_root')
    fatherFolder = None
    folderName = request.POST.get('folder_name')
    if isRoot != 1:
        fatherFolder = Folder.objects.get(folderId=request.POST.get('father_id'))
    if Folder.objects.filter(folderTeam=team, folderName=folderName, fatherFolder=fatherFolder).exists():
        return JsonResponse({'errno': 700001, 'msg': '文件夹名称重复'})
    createTime = datetime.datetime.strptime(request.POST.get('create_time'), '%Y-%m-%d %H:%M')
    Folder.objects.create(folderTeam=team, folderName=folderName, isRoot=isRoot, fatherFolder=fatherFolder,
                          folderCreator=user, createTime=createTime, lastEditTime=createTime)
    return JsonResponse({'errno': 0, 'msg': '文件夹创建成功'})


@csrf_exempt
def renameFolder(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    folderId = request.POST.get('folder_id')
    folderName = request.POST.get('folder_name')
    folders = Folder.objects.filter(folderId=folderId)
    if not folders.exists():
        return JsonResponse({'errno': 700002, 'msg': '文件夹不存在'})
    folder = folders.first()
    editTime = datetime.datetime.strptime(request.POST.get('edit_time'), '%Y-%m-%d %H:%M')
    if Folder.folderName == folderName:
        return JsonResponse({'errno': 700003, 'msg': '文件夹名称未改变'})
    if Folder.objects.filter(folderTeam=folder.folderTeam, folderName=folderName,
                             fatherFolder=folder.fatherFolder).exists():
        return JsonResponse({'errno': 700001, 'msg': '文件夹名称重复'})
    folder.folderName = folderName
    folder.lastEditTime = editTime
    folder.save()
    return JsonResponse({'errno': 0, 'msg': '文件夹重命名成功'})


@csrf_exempt
def deleteFolder(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    folderId = request.POST.get('folder_id')
    folders = Folder.objects.filter(folderId=folderId)
    if not folders.exists():
        return JsonResponse({'errno': 700002, 'msg': '文件夹不存在'})
    folder = folders.first()
    folder.delete()
    return JsonResponse({'errno': 0, 'msg': '文件夹删除成功'})


@csrf_exempt
def moveFolder(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    folderId = request.POST.get('folder_id')
    toFolderId = request.POST.get('to_folder_id')
    folders = Folder.objects.filter(folderId=folderId)
    if not folders.exists():
        return JsonResponse({'errno': 700002, 'msg': '文件夹不存在'})
    folder = folders.first()
    editTime = datetime.datetime.strptime(request.POST.get('edit_time'), '%Y-%m-%d %H:%M')
    if toFolderId == 0:
        toFolder = None
    else:
        folders = Folder.objects.filter(folderId=toFolderId)
        if not folders.exists():
            return JsonResponse({'errno': 700004, 'msg': '目标文件夹不存在'})
        toFolder = folders.first()
    if Folder.objects.filter(folderTeam=folder.folderTeam, folderName=folder.folderName,
                             fatherFolder=toFolder).exists():
        return JsonResponse({'errno': 700001, 'msg': '文件夹名称重复'})
    folder.fatherFolder = toFolder
    folder.lastEditTime = editTime
    if toFolderId == 0:
        folder.isRoot = 1
    folder.save()
    return JsonResponse({'errno': 0, 'msg': '文件夹移动成功'})


@csrf_exempt
def moveFile(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    fileId = request.POST.get('file_id')
    toFolderId = request.POST.get('to_folder_id')
    files = File.objects.filter(fileId=fileId)
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    if toFolderId == 0:
        toFolder = None
    else:
        folders = Folder.objects.filter(folderId=toFolderId)
        if not folders.exists():
            return JsonResponse({'errno': 700004, 'msg': '目标文件夹不存在'})
        toFolder = folders.first()
    if File.objects.filter(fileName=file.fileName, judge=1, fileTeam=file.fileTeam,
                           fileFolder=file.fileFolder).exists():
        return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
    editTimeStr = request.POST.get('edit_time')
    editTime = datetime.datetime.strptime(editTimeStr, '%Y-%m-%d %H:%M')
    file.fileFolder = toFolder
    file.lastEditTime = editTimeStr
    file.lastEditUser = user
    file.lastEditTimeRecord = editTime
    file.save()
    return JsonResponse({'errno': 0, 'msg': '文档移动成功'})


@csrf_exempt
def file_center(request):
    if request.method == 'POST':
        request.META.get('HTTP_USREID')
        teamid = request.POST.get('teamid')
        team = Team.objects.get(teamid=teamid)
        team_files = File.objects.filter(fileTeam=team, judge=1)
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


def getFolderContent(folderId):
    thisFolder = Folder.objects.get(folderId=folderId)
    content = []
    folderList = Folder.objects.filter(fatherFolder=thisFolder).order_by('-lastEditTime')
    fileList = File.objects.filter(fileFolder=thisFolder).order_by('-lastEditTimeRecord')
    for folder in folderList:
        content.append({
            'type': 1,
            'folder_id': int(folder.folderId),
            'last_edit_time': folder.lastEditTime.strptime('%Y-%m-%d %H:%M'),
            'content': getFolderContent(int(folder.folderId))
        })
    for file in fileList:
        content.append({
            'type': 2,
            'file_id': int(file.fileId),
            'last_edit_time': file.lastEditTime,
        })
