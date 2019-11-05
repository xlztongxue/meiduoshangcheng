from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from meiduo_admin.serializers.users import UserSerializer
from users.models import User




# 用户管理查询用户
class UserInfoView(ListCreateAPIView):
    # 用户登录认证
    permission_classes = [IsAdminUser]
    # 指定视图所使用的序列化器类
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('id')

    # 重写查询集方法
    def get_queryset(self):
        """
           获取普通用户数据:
           1. 获取keyword关键字
           2. 查询普通用户数据
           3. 将用户数据序列化并返回
       """
        # 1.获取keyword关键字
        keyword = self.request.query_params.get('keyword')
        # 2. 查询普通用户数据
        if not keyword:
            return self.queryset
        else:
            return self.queryset.filter(username__contains=keyword)



