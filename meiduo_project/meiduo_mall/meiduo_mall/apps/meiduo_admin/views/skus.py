from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU, GoodsCategory, SPU
from meiduo_admin.serializers.categorys import CategoriesSerializer
from meiduo_admin.serializers.options import SpuSpecSerializer
from meiduo_admin.serializers.skus import SKUSerializer


class SkusViewSet(ModelViewSet):
    """规格商品的增删改查"""
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = SKU.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = SKUSerializer

    # 指定router动态生成路由时，提取参数的正则表达式
    lookup_value_regex = '\d+'

    # 重写获取查询集数据的方法
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if not keyword:
            return self.queryset
        else:
            return self.queryset.filter(name__contains=self.request.query_params.get('keyword'))


    @action(methods=['get'], detail=False)
    def categories(self, request):
        """查询三级分类"""
        # 查询规格选项商品
        # 方式一
        # categories = GoodsCategory.objects.filter(subs__id=None)
        # 方式二
        categories = GoodsCategory.objects.filter(subs__isnull=True)
        # 序列化返回数据
        ser = CategoriesSerializer(categories, many=True)
        # 返回结果
        return Response(ser.data)


    def specs(self, request, pk):
        """查询规格信息"""
        """
        获取spu商品规格信息
        :param request:
        :param pk:  spu表id值
        :return:
        """

        # 1、查询spu对象
        spu = SPU.objects.get(id=pk)
        # 2、关联查询spu所关联的规格表
        data = spu.specs.all()
        # 3、序列化返回规格信息
        ser = SpuSpecSerializer(data, many=True)
        return Response(ser.data)



