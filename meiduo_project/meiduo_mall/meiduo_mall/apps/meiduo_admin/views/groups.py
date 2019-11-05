from django.contrib.auth.models import Group, Permission
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.groups import GroupSerializer
from meiduo_admin.serializers.permissions import PermissionSerializer


class GroupViewSet(ModelViewSet):
    """权限管理"""
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = Group.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = GroupSerializer


    def simple(self, request):
        """查询用户权限信息"""
        # 1.查询权限表
        data = Permission.objects.all()
        # 2.返回权限数据
        ser = PermissionSerializer(data, many=True)
        return Response(ser.data)
