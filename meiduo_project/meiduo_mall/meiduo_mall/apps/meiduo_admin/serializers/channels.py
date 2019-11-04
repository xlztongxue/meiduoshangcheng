from rest_framework import serializers
from goods.models import GoodsCategory, GoodsChannelGroup, GoodsChannel


class ChannelSerializer(serializers.ModelSerializer):
    """商品频道组序列化器"""
    # 关联对象嵌套序列化
    category = serializers.StringRelatedField(label='一级分类名称', read_only=True)
    group = serializers.StringRelatedField(label="频道组名称", read_only=True)

    category_id = serializers.IntegerField(label='一级分类ID')
    group_id = serializers.IntegerField(label='频道组ID')


    class Meta:
        model = GoodsChannel
        exclude = ('create_time', 'update_time')

class ChannelGroupSerializer(serializers.ModelSerializer):
    """商品频道组名"""
    class Meta:
        model = GoodsChannelGroup
        fields = ('id', 'name')



class FirstCategoriesSerializer(serializers.ModelSerializer):
    """商品类别"""
    class Meta:
        model = GoodsCategory
        exclude = ('create_time', 'update_time', 'parent')
