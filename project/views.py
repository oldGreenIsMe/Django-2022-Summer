from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.models import *


@csrf_exempt
def rename_project(request):
    if request.method != 'POST':
        return JsonResponse({'errno': 200001, 'msg': '请求方式错误'})
    users = User.objects.filter(userid=request.META.get('HTTP_USERID'))
    if not users.exists():
        return JsonResponse({'errno': 50001, 'msg': '请登录'})
    projid = request.POST.get('projId')
    projs = Project.objects.filter(projId=projid)
    if not projs.exists():
        return JsonResponse({'errno': 300001, 'msg': '项目不存在'})
    newname = request.POST.get('newName')
    if newname is None or newname == '':
        return JsonResponse({'errno': 400001, 'msg': '名称不能为空'})

    Project.objects.filter(projId=projid).update(projName=newname)
    return JsonResponse({'errno': 0, 'msg': '修改成功'})

