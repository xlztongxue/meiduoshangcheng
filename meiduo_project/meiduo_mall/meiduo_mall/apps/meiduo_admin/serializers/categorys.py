from rest_framework import serializers

from goods.models import GoodsCategory


class CategoriesSerializer(serializers.ModelSerializer):
    """商品类别"""
    class Meta:
        model = GoodsCategory
        fields = '__all__'