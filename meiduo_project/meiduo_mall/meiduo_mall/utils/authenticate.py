from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from datetime import datetime
from users.models import User
from users.utils import get_user_by_account

class UsernameMobileBackend(ModelBackend):
    """自定义用户认证后端"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写父类方法
        :param request: 请求对象
        :param username: 用户名
        :param password: 密码
        :param kwargs: 其它参数
        :return: user
        """
        if request is None:
            # 后台登录
            user = User.objects.filter(Q(username=username) | Q(email=username), is_staff=True).first()
            if user is not None and user.check_password(password):
                # 设置最新登录时间
                user.last_login = datetime.now()
                user.save()
                return user

        else:
            # 前台登录
            # 根据传入的username 获取user对象
            user = get_user_by_account(username)
            # 校验user是否存在并校验密码是否正确
            if user and user.check_password(password):
                return user
            else:
                return None

