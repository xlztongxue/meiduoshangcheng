from rest_framework import serializers

from goods.models import GoodsCategory


class CategoriesSerializer(serializers.ModelSerializer):
    """商品类别"""
    name = serializers.StringRelatedField(read_only=True)
    parent = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GoodsCategory
        fields = '__all__'



class CategorieSerializer(serializers.ModelSerializer):
    """商品类别"""
    subs = CategoriesSerializer(read_only=True, many=True)
    class Meta:
        model = GoodsCategory
        fields = '__all__'