import re

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SPU, Brand, GoodsCategory
from meiduo_admin.serializers.brands import BrandsSerializer
from meiduo_admin.serializers.categorys import CategoriesSerializer, CategorieSerializer
from meiduo_admin.serializers.spus import SPUSerializer


class SPUViewSet(ModelViewSet):
    """规格商品的增删改查"""
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = SPU.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = SPUSerializer
    # 指定router动态生成路由时，提取参数的正则表达式
    lookup_value_regex = '\d+'

    def simple(self, request):
        """查询品牌信息"""
        data = Brand.objects.all()
        ser = BrandsSerializer(data, many=True)
        return Response(ser.data)

    def get_category(self, request):
        """查询一级分类ID"""
        # 查询一级分类ID
        category = GoodsCategory.objects.filter(parent=None)
        # 序列化返回数据
        ser = CategoriesSerializer(category, many=True)
        # 返回结果
        return Response(ser.data)

    def get_categories(self, request, pk):
        """查询二级分类ID"""
        # 查询一级分类ID
        category = GoodsCategory.objects.get(pk=pk)
        # 序列化返回数据
        ser = CategorieSerializer(category)
        # 返回结果
        return Response(ser.data)



