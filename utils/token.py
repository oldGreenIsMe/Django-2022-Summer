import time
import hashlib
from django.core import signing
from django.conf import settings

HEADER = {'typ': 'JWT', 'alg': 'HS256'}
KEY = settings.SECRETS['signing']['key']
SALT = settings.SECRETS['signing']['salt']


# 加密
def encrypt(obj):
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


# 解密
def decrypt(src):
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    return raw


# 生成token信息
def create_token(userid):
    # 1.加密头信息
    header = encrypt(HEADER)
    # 2.构造Payload(有效期1天)
    payload = {"userid": userid, "iat": time.time(), "exp": time.time()+86400.0}
    payload = encrypt(payload)
    # 3.生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    return token


def get_payload(token):
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload


# 通过token获取用户id
def get_userid(token):
    payload = get_payload(token)
    return payload['userid']


def get_exp_time(token):
    payload = get_payload(token)
    return payload['exp']


def check_token(userid, token):
    return get_userid(token) == userid and get_exp_time(token) > time.time()
