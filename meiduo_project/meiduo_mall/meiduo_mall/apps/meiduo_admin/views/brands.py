from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import Brand
from meiduo_admin.serializers.brands import BrandsSerializer


class BrandsViewSet(ModelViewSet):
    """品牌增删改查"""
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = Brand.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = BrandsSerializer
