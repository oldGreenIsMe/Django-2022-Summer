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
        authorizeAdminNotice(creator.username, user.username, team.teamname, user.email)
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
    InviteMessage.objects.create(team=team, user=user, inviter=admin, timeOrder=timezone.now() +
                                                                                datetime.timedelta(hours=8))
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
        if not UserTeam.objects.filter(user=user, team=team).exists():
            return JsonResponse({'errno': 300020, 'msg': '用户不在团队中'})
        user_team = UserTeam.objects.get(user=user, team=team)
        if user_team.permission == 0:
            user.team_belonged.remove(team)
        else:
            return JsonResponse({'errno': 300005, 'msg': '被删用户是管理员，无法被删除'})
        deleteNotice(admin.username, user.username, team.teamname, user.email)
        InviteMessage.objects.create(team=team, inviter=admin, user=user, timeOrder=timezone.now() +
                                                                                    datetime.timedelta(hours=8), type=3)
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
            'proj_info': proj.projInfo,
            'start_time': proj.startTime,
            'end_time': proj.endTime
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
        if not Team.objects.filter(teamid=teamid):
            return JsonResponse({'errno': 300019, 'msg': '团队不存在'})
        team = Team.objects.get(teamid=teamid)
        user_team = UserTeam.objects.get(user=user, team=team)
        if user_team.permission != 2:
            return JsonResponse({'errno': 300010, 'msg': '非创造者，无权限删除队伍'})
        users = UserTeam.objects.filter(team=team)
        time = timezone.now() + datetime.timedelta(hours=8)
        for user0 in users:
            if user0.user != user:
                deleteTeamNotice(user.username, user0.user.username, team.teamname, user0.user.email)
                InviteMessage.objects.create(team=None, inviter=user, user=user0.user, timeOrder=time, type=4,
                                             deleteTeamName=team.teamname)
            else:
                InviteMessage.objects.create(team=None, inviter=user, user=user0.user, timeOrder=time, type=4,
                                             readStatus=2, deleteTeamName=team.teamname)
        team.delete()
        return JsonResponse({'errno': 0, 'msg': '删除团队成功'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def handleInvitation(request):
    if request.method == 'POST':
        inviteId = int(request.POST.get('inviteId'))
        inviteMessage = InviteMessage.objects.get(inviteId=inviteId)
        user = inviteMessage.user
        team = inviteMessage.team
        type = int(request.POST.get('type'))
        if type == 1 and not UserTeam.objects.filter(user=user, team=team).exists():
            UserTeam.objects.create(user=user, team=team, permission=0)
        nowTime = timezone.now() + datetime.timedelta(hours=8)
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
        userTeamList = UserTeam.objects.filter(team=team).filter(Q(permission=1) | Q(permission=2))
        nowTime = timezone.now() + datetime.timedelta(hours=8)
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
    if returnVal == -1:
        return JsonResponse({'errno': 300017, 'msg': '邮箱域名无效，发送验证码失败'})
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
    nowTime = timezone.now() + datetime.timedelta(hours=8)
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
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500010, 'msg': '没有权限执行该信操作'})
    isRoot = int(request.POST.get('is_root'))
    fatherFolder = None
    folderName = request.POST.get('folder_name')
    if isRoot != 1:
        fatherFolder = Folder.objects.get(folderId=request.POST.get('father_id'))
    if Folder.objects.filter(folderTeam=team, folderName=folderName, fatherFolder=fatherFolder).exists():
        return JsonResponse({'errno': 700001, 'msg': '文件夹名称重复'})
    createTime = datetime.datetime.strptime(request.POST.get('create_time'), '%Y-%m-%d %H:%M:%S')
    createTime = createTime + datetime.timedelta(hours=8)
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
    team = folder.folderTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500010, 'msg': '没有权限进行该操作'})
    editTime = datetime.datetime.strptime(request.POST.get('edit_time'), '%Y-%m-%d %H:%M:%S')
    editTime = editTime + datetime.timedelta(hours=8)
    if folder.folderName == folderName:
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
    team = folder.folderTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500010, 'msg': '没有权限执行该操作'})
    folder.delete()
    return JsonResponse({'errno': 0, 'msg': '文件夹删除成功'})


@csrf_exempt
def moveFolder(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    folderId = request.POST.get('folder_id')
    toFolderId = int(request.POST.get('to_folder_id'))
    folders = Folder.objects.filter(folderId=folderId)
    if not folders.exists():
        return JsonResponse({'errno': 700002, 'msg': '文件夹不存在'})
    folder = folders.first()
    team = folder.folderTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500010, 'msg': '没有权限执行该操作'})
    editTime = datetime.datetime.strptime(request.POST.get('edit_time'), '%Y-%m-%d %H:%M:%S')
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
    folder.lastEditTime = editTime + datetime.timedelta(hours=8)
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
    toFolderId = int(request.POST.get('to_folder_id'))
    files = File.objects.filter(fileId=fileId)
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    team = file.fileTeam
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500010, 'msg': '没有权限执行该操作'})
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
    editTime = datetime.datetime.strptime(editTimeStr, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    file.fileFolder = toFolder
    file.lastEditTime = editTimeStr
    file.lastEditUser = user
    file.lastEditTimeRecord = editTime
    file.save()
    return JsonResponse({'errno': 0, 'msg': '文档移动成功'})


@csrf_exempt
def copyFolder(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    folderId = request.POST.get('folder_id')
    toFolderId = int(request.POST.get('to_folder_id'))
    editTimeStr = request.POST.get('edit_time')
    editTime = datetime.datetime.strptime(editTimeStr, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    folders = Folder.objects.filter(folderId=folderId)
    if not folders.exists():
        return JsonResponse({'errno': 700002, 'msg': '文件夹不存在'})
    folder = folders.first()
    team = folder.folderTeam
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500010, 'msg': '没有权限执行该操作'})
    isRoot = 2
    if toFolderId == 0:
        toFolder = None
        isRoot = 1
    else:
        folders = Folder.objects.filter(folderId=toFolderId)
        if not folders.exists():
            return JsonResponse({'errno': 700004, 'msg': '目标文件夹不存在'})
        toFolder = folders.first()
    newName = folder.folderName
    if toFolder != folder.fatherFolder:
        if Folder.objects.filter(folderTeam=folder.folderTeam, folderName=newName, fatherFolder=toFolder).exists():
            return JsonResponse({'errno': 700001, 'msg': '文件夹名称重复'})
    else:
        i = 1
        while Folder.objects.filter(folderTeam=folder.folderTeam, folderName=newName, fatherFolder=toFolder).exists():
            newName = folder.folderName + '(' + str(i) + ')'
            i += 1
    newFolder = Folder(folderTeam=folder.folderTeam, folderName=newName, isRoot=isRoot, fatherFolder=toFolder,
                       folderCreator=user, createTime=editTime, lastEditTime=editTime)
    newFolder.save()
    copyFolderMethod(folder, newFolder, editTimeStr, editTime, user)
    return JsonResponse({'errno': 0, 'msg': '文件夹复制成功'})


@csrf_exempt
def copyTeamFile(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    fileId = request.POST.get('file_id')
    toFolderId = int(request.POST.get('to_folder_id'))
    editTimeStr = request.POST.get('edit_time')
    editTime = datetime.datetime.strptime(editTimeStr, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    files = File.objects.filter(fileId=fileId)
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    team = file.fileTeam
    if not UserTeam.objects.filter(user=user, team=team).exists():
        return JsonResponse({'errno': 500010, 'msg': '没有权限执行该操作'})
    if toFolderId == 0:
        toFolder = None
    else:
        folders = Folder.objects.filter(folderId=toFolderId)
        if not folders.exists():
            return JsonResponse({'errno': 700004, 'msg': '目标文件夹不存在'})
        toFolder = folders.first()
        if toFolder.folderTeam.teamid != team.teamid:
            return JsonResponse({'errno': 500010, 'msg': '没有权限执行该操作'})
    newName = file.fileName
    if toFolder != file.fileFolder:
        if File.objects.filter(fileName=newName, judge=1, fileTeam=file.fileTeam, fileFolder=toFolder).exists():
            return JsonResponse({'errno': 400003, 'msg': '文档名称重复'})
    else:
        i = 1
        while File.objects.filter(fileName=newName, judge=1, fileTeam=file.fileTeam, fileFolder=toFolder).exists():
            newName = file.fileName + '(' + str(i) + ')'
            i += 1
    File.objects.create(fileName=newName, fileCreator=user, content=file.content, create=editTimeStr,
                        lastEditTime=editTimeStr, lastEditUser=user, lastEditTimeRecord=editTime,
                        judge=1, fileTeam=file.fileTeam, fileFolder=toFolder, new=2, file_model=file.file_model)
    return JsonResponse({'errno': 0, 'msg': '文档复制成功'})


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
def deleteTeamFile(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    fileId = request.POST.get('file_id')
    files = File.objects.filter(fileId=fileId)
    if not files.exists():
        return JsonResponse({'errno': 400004, 'msg': '文档不存在'})
    file = files.first()
    file.delete()
    return JsonResponse({'errno': 0, 'msg': '团队文档删除成功'})


@csrf_exempt
def file_center(request):
    if request.method == 'POST':
        teamId = request.POST.get('teamid')
        team = Team.objects.get(teamid=teamId)
        user = User.objects.get(userid=request.META.get('HTTP_USERID'))
        if not UserTeam.objects.filter(user=user, team=team).exists():
            return JsonResponse({'errno': 500010, 'msg': '没有权限执行该操作'})
        teamData = getFolderContent(0, team)
        projects = Project.objects.filter(projTeam=team, status=1)
        projects_data = []
        for project in projects:
            files_data = []
            files = File.objects.filter(projectId=project, judge=0)
            for file in files:
                files_data.append({
                    'file_id': file.fileId,
                    'file_name': file.fileName,
                    'file_flag': 0,
                    'type_flag': 0,
                    'last_edit_time': file.lastEditTime,
                    'project_id': project.projId
                })
            projects_data.append({
                'projectId': project.projId,
                'projName': project.projName,
                'type_flag': 0,
                'files_data': files_data
            })
        return JsonResponse({'errno': 0, 'team_data': teamData, 'project_data': projects_data})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


def getFolderContent(folderId, team):
    data = []
    if folderId == 0:
        thisFolder = None
    else:
        thisFolder = Folder.objects.get(folderId=folderId)
    folders = Folder.objects.filter(folderTeam=team, fatherFolder=thisFolder).order_by('-lastEditTime')
    files = File.objects.filter(fileTeam=team, fileFolder=thisFolder, judge=1).order_by('-lastEditTimeRecord')
    for folder in folders:
        midId = 0
        if folder.fatherFolder is not None:
            midId = folder.fatherFolder.folderId
        data.append({
            'file_id': int(folder.folderId),
            'file_name': folder.folderName,
            'file_flag': 1,
            'type_flag': 1,
            'last_edit_time': folder.lastEditTime.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_folder_id': midId,
            'file_list': getFolderContent(folder.folderId, folder.folderTeam)
        })
    for file in files:
        midId = 0
        if file.fileFolder is not None:
            midId = file.fileFolder.folderId
        data.append({
            'file_id': int(file.fileId),
            'file_name': file.fileName,
            'file_flag': 0,
            'type_flag': 1,
            'last_edit_time': file.lastEditTime,
            'parent_folder_id': midId,
            'file_list': []
        })
    return data


def copyFolderMethod(oldFolder, newFolder, timeStr, time, user):
    folderList = Folder.objects.filter(folderTeam=oldFolder.folderTeam, fatherFolder=oldFolder)
    fileList = File.objects.filter(judge=1, fileTeam=oldFolder.folderTeam, fileFolder=oldFolder)
    for folder in folderList:
        midNewFolder = Folder(folderTeam=folder.folderTeam, folderName=folder.folderName, isRoot=2,
                              fatherFolder=newFolder, folderCreator=folder.folderCreator, createTime=time,
                              lastEditTime=time)
        midNewFolder.save()
        copyFolderMethod(folder, midNewFolder, timeStr, time, user)
    for file in fileList:
        File.objects.create(fileName=file.fileName, fileCreator=file.fileCreator, content=file.content, create=timeStr,
                            lastEditTime=timeStr, lastEditUser=user, lastEditTimeRecord=time, judge=1,
                            fileTeam=file.fileTeam, fileFolder=newFolder, new=2, file_model=file.file_model)
