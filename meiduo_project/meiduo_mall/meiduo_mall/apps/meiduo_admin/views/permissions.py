from django.contrib.auth.models import Permission, ContentType
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.permissions import PermissionSerializer, ContentTypeSerializer


class PermissionViewSet(ModelViewSet):
    """权限管理"""
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = Permission.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = PermissionSerializer


    def content_type(self, request):
        """查询权限类型"""
        # 1、查询content_type对象
        data = ContentType.objects.all()
        # 2、序列化返回权限类型信息
        ser = ContentTypeSerializer(data, many=True)
        return Response(ser.data)