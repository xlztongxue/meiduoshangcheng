from rest_framework import serializers

from goods.models import SKUImage, SKU


class SkuImageSerialzier(serializers.ModelSerializer):
    """SKU图片序列化器"""
    class Meta:
        model = SKUImage
        fields = ('__all__')



class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    class Meta:
        model = SKU
        fields = ('__all__')