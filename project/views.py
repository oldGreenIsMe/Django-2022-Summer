from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *


@csrf_exempt
def createProj(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    projName = request.POST.get('proj_name')
    user = User.objects.get(userid=request.META.get('HTTP_USERID'))
    projTeam = Team.objects.get(teamid=request.POST.get('team_id'))
    projects = Project.objects.filter(projName=projName, projTeam=projTeam)
    if projects.exists():
        return JsonResponse({'errno': 400001, 'msg': '项目名称重复'})
    project = Project(projName=projName, projCreator=user, projTeam=projTeam, deletePerson=None, deleteTime=None)
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
    return JsonResponse({'errno': 0, 'msg': '项目删除成功'})
