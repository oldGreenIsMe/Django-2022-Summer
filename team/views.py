from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from team.models import User, Team, UserTeam
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
        users = User.objects.filter(userid=userid)
        if users.exists():
            user = users.first()
            if user.password == password:
                token = create_token(userid)
                return JsonResponse({
                    'errno': 0,
                    'msg': '登录成功',
                    'data': {
                        'username': user.username,
                        'authorization': token,
                        'userid': user.userid,
                        'photo': user.photo.url,
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
    if request.method == 'POST':
        adminid = request.META.get('HTTP_USERID')
        admin = User.objects.get(userid=adminid)
        teamid = request.POST.get('teamid')
        team = Team.objects.get(teamid=teamid)
        admin_team = UserTeam.objects.get(user=admin, team=team)
        if admin_team.permission == 0:
            return JsonResponse({'errno': 300004, 'msg':'非管理员，没有操作权限'})
        userid = request.POST.get('userid')
        user = User.objects.get(userid=userid)
        UserTeam.objects.create(user=user, team=team, permission=0)
        return JsonResponse({'errno': 0, 'msg': '邀请成员成功'})
    else:
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})


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
        projs = team.project_set.all()
        projs_data = []
        for proj in projs:
            projs_data.append({'proj_id': proj.projID, 'proj_name': proj.projName})
        data.append({
            'teamname': team.teamname,
            'teamid': team.teamid,
            'proj': projs_data
        })
    return JsonResponse({
        'data': data
    })

@csrf_exempt
def teamspace(request):
    userid = request.META.get('HTTP_USERID')
    user = User.objects.get(userid=userid)
    teamid = request.POST.get('teamid')
    team = Team.objects.get(teamid=teamid)
    user_teams = UserTeam.objects.filter(user=user,team=team)
    if not user_teams.exists():
        return JsonResponse({'errno': 300006, 'msg': '您尚未加入该团队'})
    user_team = user_teams.first()
    projs = team.project_set.all()
    # 将项目信息放入projdata
    projdata = []
    for proj in projs:
        projdata.append({
            'proj_id': proj.projID,
            'proj_name': proj.projName,
            'proj_photo': proj.photo
        })
    members = team.user_set.all()
    memberdata = []
    for member in members:
        memberdata.append({
            'member_id': member.userid,
            'member_name': member.username,
            'member_photo': member.photo.url
        })
    return JsonResponse({'projs': projdata, 'members': memberdata, 'permission': user_team.permission})


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
        memberdata.append({
            'member_id': member.userid,
            'member_name': member.username,
            'member_photo': member.photo.url
        })
    return JsonResponse({
        'permission': user_team.permission,
        'members': memberdata
    })