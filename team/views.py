from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from team.models import User
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
        User.objects.create(username=username, password=password_1, truename=truename, email=email)
        return JsonResponse({'errno': 0, 'msg': '注册成功'})
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
