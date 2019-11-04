from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU, SKUImage
from meiduo_admin.serializers.images import SkuImageSerialzier, SKUSerializer


class ImagesViewSet(ModelViewSet):
    # 验证用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = SKUImage.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = SkuImageSerialzier

    def simple(self, request):
        """获取SPU商品"""
        # 查询skus商品
        skus = SKU.objects.all()
        # 序列化返回数据
        ser = SKUSerializer(skus, many=True)
        # 返回结果
        return Response(ser.data)

