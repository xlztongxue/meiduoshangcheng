from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import SPUSpecification
from meiduo_admin.serializers.goods import SpecsSerialzier



class SpecsViewSet(ModelViewSet):
    """规格商品的增删改查"""
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = SPUSpecification.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = SpecsSerialzier