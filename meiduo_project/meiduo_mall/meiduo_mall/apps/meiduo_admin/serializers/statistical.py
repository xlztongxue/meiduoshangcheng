from rest_framework import serializers

# 分类商品浏览记录
from goods.models import GoodsVisitCount


# 分类商品浏览反序列化器类
class GoodsVisitSerializer(serializers.ModelSerializer):

    # 关联对象嵌套序列化：将关联对象序列化为关联对象模型类__str__方法的返回值
    category = serializers.StringRelatedField(label='分类')

    class Meta:
        # 指定模型
        model = GoodsVisitCount
        # 指定字段
        fields = ('category', 'count')

