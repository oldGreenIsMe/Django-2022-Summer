from utils.token import check_token
from django.http import JsonResponse

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object


API_WHITELIST = ["/api/team/register", "/api/team/login", "/api/team/sendVerifyCode", "/api/team/acceptInvitation",
                 "/api/project/get_pdf"]


class AuthorizeMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        if request.path not in API_WHITELIST:
            userid = request.META.get('HTTP_USERID')
            token = request.META.get('HTTP_TOKEN')
            if userid is None or token is None:
                return JsonResponse({'errno': 100001, 'msg': "未查询到登录信息"})
            else:
                if check_token(userid, token):
                    pass
                else:
                    return JsonResponse({'errno': 100002, 'msg': "登录信息错误或已过期"})
