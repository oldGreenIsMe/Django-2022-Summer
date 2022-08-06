from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from team.models import *
from utils.email import *
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
        users = User.objects.filter(email=email)
        if users.exists():
            return JsonResponse({'errno': 300007, 'msg': '邮箱已注册'})
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
    InviteMessage.objects.create(team=team, user=user, inviter=admin)
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
def accept_invite(request):
    if request.method == 'POST':
        inviteId = request.POST.get('inviteId')
        inviteMessage = InviteMessage.objects.get(inviteId=inviteId)
        now_user = User.objects.get(userid=request.META.get('HTTP_USERID'))
        user = inviteMessage.user
        team = inviteMessage.team
        user_teams = UserTeam.objects.filter(user=user, team=team)
        if user_teams.exists():
            inviteMessage.delete()
            return JsonResponse({'errno': 300013, 'msg': '用户已在团队中'})
        if user != now_user:
            # 当用户是在teamspace中看到申请
            nowuser_team = UserTeam.objects.get(user=now_user, team=team)
            if nowuser_team.permission == 0:
                return JsonResponse({'errno': 300014, 'msg': '用户权限不够'})
        UserTeam.objects.create(user=user, team=team, permission=0)
        inviteMessage.delete()
        msg = user.username + '加入团队成功'
        return JsonResponse({'errno': 0, 'msg': msg})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def refuse_invite(request):
    if request.method == 'POST':
        inviteId = request.POST.get('inviteId')
        inviteMessages = InviteMessage.objects.filter(inviteId=inviteId)
        if not inviteMessages.exists():
            return JsonResponse({'errno': 300011, 'msg': '邀请信息已失效'})
        inviteMessage = inviteMessages.first()
        now_user = User.objects.get(userid=request.META.get('HTTP_USERID'))
        if now_user != inviteMessage.user:
            # 当用户是在teamspace中看到申请
            nowuser_team = UserTeam.objects.get(user=now_user, team=inviteMessage.team)
            if nowuser_team.permission == 0:
                return JsonResponse({'errno': 300014, 'msg': '用户权限不够'})
        inviteMessage.delete()
        return JsonResponse({'errno': 0, 'msg': '邀请已删除'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def search_team(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        teams = Team.objects.filter(teamname_icontains=name)
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
        messages = InviteMessage.objects.filter(user=user, team=team)
        if messages.exists():
            return JsonResponse({'errno': 300012, 'msg': '申请已存在'})
        InviteMessage.objects.create(team=team, user=user)
        return JsonResponse({'errno': 0, 'msg': '申请已发送'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


@csrf_exempt
def search_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        users = User.objects.filter(username_icontains=name)
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
    judge = int(request.POST.get('judge'))
    returnVal = sendVerifyCodeMethod(email, judge)
    return JsonResponse({'errno': 0, 'msg': '验证码发送成功', 'code': returnVal})


@csrf_exempt
def acceptInvitation(request):
    token = request.GET.get('token')
    data = inviteMemberCheck(token)
    teamId = data['teamid']
    userId = data['userid']
    return render(request, 'jumpPage.html')
