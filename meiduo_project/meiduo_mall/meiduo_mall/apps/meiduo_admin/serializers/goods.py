from rest_framework import serializers
from goods.models import SPUSpecification, SKUImage, SKU
from goods.models import SPU

class SpecsSerialzier(serializers.ModelSerializer):
    """规格序列化器"""

    # 指定关联外键返回形式
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()
    class Meta:
        model = SPUSpecification
        fields = ('__all__')


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化器"""
    class Meta:
        model = SPU
        fields = ('__all__')


class SkuImageSerialzier(serializers.ModelSerializer):
    """SKU图片序列化器"""
    sku_id = serializers.IntegerField()
    class Meta:
        model = SKUImage
        fields = ('__all__')


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    class Meta:
        model = SKU
        fields = ('__all__')

