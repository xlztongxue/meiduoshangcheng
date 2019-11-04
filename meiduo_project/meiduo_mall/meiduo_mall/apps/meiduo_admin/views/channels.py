from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import GoodsChannel
from meiduo_admin.serializers.channels import ChannelSerializer


class ChannelsViewSet(ModelViewSet):
    """商品频道管理"""
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = GoodsChannel.objects.all().order_by('id')
    # 2.指定序列化器
    serializer_class = ChannelSerializer