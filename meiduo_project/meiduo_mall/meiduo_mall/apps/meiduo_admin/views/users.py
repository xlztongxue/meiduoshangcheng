from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView

from meiduo_admin.serializers.users import AdminAuthSerializer

# POST /meiduo_admin/authorizations/

# 用户登录视图
class AdminAuthorizeView(CreateAPIView):
    # 指定当前视图所使用的序列化器类
    serializer_class = AdminAuthSerializer

