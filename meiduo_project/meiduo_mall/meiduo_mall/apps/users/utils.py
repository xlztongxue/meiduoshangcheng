# 自定义多帐号登录的后端：实现多帐号登录
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
import re
from .views import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from . import constants



def check_verify_token(token):
    """
    反序列化token
    :param token: 序列化后的信息
    :return: user
    """
    s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        print(token)
        data = s.loads(token)
    except BadData as e:
        print(e)
        return None
    else:
        # 从data中取出user_id和email
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def generate_verfy_email_url(user):
    """
    生成激活链接
    :param user: 当前登录用户
    :return: token 链接
    """
    # s = Serialzier('秘钥:越复杂越安全', '过期时间')
    s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id':user.id, 'email':user.email}
    token = s.dumps(data)
    print(token.decode())
    return settings.EMAIL_VERIFT_URL + "?token=" + token.decode()


def get_user_by_account(account):
    """
    根据account查询用户
    :param account: 用户名或者手机号
    :return: user
    """
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # 手机号登录
            user = User.objects.get(mobile=account)
        else:
            # 用户名登录
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user

