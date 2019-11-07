from rest_framework import serializers

from goods.models import Brand


class BrandsSerializer(serializers.ModelSerializer):
    """品牌序列化器"""
    class Meta:
        model = Brand
        fields = '__all__'