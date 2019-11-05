from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SpecificationOption, SPUSpecification
from meiduo_admin.serializers.options import OptionSerializer, SpuSpecificationSerializer


class OptionsViewSet(ModelViewSet):
    """商品频道管理"""
    # 验证用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = SpecificationOption.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = OptionSerializer


    def simple(self, requset):
        """查询规格选项"""
        # 查询规格选项商品
        spus = SPUSpecification.objects.all()
        # 序列化返回数据
        ser = SpuSpecificationSerializer(spus, many=True)

        # 返回结果
        return Response(ser.data)
