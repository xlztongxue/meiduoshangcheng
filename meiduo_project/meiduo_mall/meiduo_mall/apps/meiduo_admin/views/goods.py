from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SPUSpecification, SPU, SKUImage, SKU
from meiduo_admin.serializers.goods import SpecsSerialzier, SPUSerializer
from meiduo_admin.serializers.goods import SkuImageSerialzier, SKUSerializer


class ImagesViewSet(ModelViewSet):
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = SKUImage.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = SkuImageSerialzier

    def simple(self, request):
        """获取SPU商品"""
        skus = SKU.objects.all()
        ser = SKUSerializer(skus, many=True)
        return Response(ser.data)

    # 逻辑删除
    def destroy(self, request, *args, **kwargs):
        sku = self.get_object()
        sku.is_delete = True
        sku.save()




class SpecsViewSet(ModelViewSet):
    """规格商品的增删改查"""
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = SPUSpecification.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = SpecsSerialzier

    def simple(self, request):
        """获取SPU商品"""
        spus = SPU.objects.all()
        ser = SPUSerializer(spus, many=True)
        return Response(ser.data)

    # 逻辑删除
    def destroy(self, request, *args, **kwargs):
        spec = self.get_object()
        spec.is_delete = True
        spec.save()





