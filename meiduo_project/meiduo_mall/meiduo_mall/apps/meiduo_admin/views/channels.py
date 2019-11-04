from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from meiduo_admin.serializers.channels import ChannelSerializer, FirstCategoriesSerializer, ChannelGroupSerializer


class ChannelsViewSet(ModelViewSet):
    """商品频道管理"""
    # 验证用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = GoodsChannel.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = ChannelSerializer

    def get_channel_types(self, request):
        """查询频道组"""
        # 查询频道组
        channel_type = GoodsChannelGroup.objects.all()
        # 序列化返回数据
        ser =  ChannelGroupSerializer(channel_type, many=True)
        # 返回结果
        return Response(ser.data)


    def get_first_categories(self, request):
        """查询一级分类ID"""
        # 查询一级分类ID
        channel_type = GoodsCategory.objects.filter(parent=None)
        # 序列化返回数据
        ser = FirstCategoriesSerializer(channel_type, many=True)
        # 返回结果
        return Response(ser.data)
