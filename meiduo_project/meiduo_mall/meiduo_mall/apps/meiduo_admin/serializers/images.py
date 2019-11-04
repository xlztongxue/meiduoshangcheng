from rest_framework import serializers

from goods.models import SKUImage, SKU


class SkuImageSerialzier(serializers.ModelSerializer):
    """SKU图片序列化器"""
    class Meta:
        model = SKUImage
        fields = ('__all__')

    def validate_sku_id(self, value):
        # sku商品是否存在
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value

    def create(self, validated_data):
        """sku商品上传图片保存"""
        # 调用ModelSerializer中的create方法
        sku_image = super().create(validated_data)
        # 保存上传图片记录
        sku = SKU.objects.get(id=validated_data['sku'].id)
        # 设置其默认图片
        sku.default_image = sku_image.image
        sku.save()
        return sku_image

class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    class Meta:
        model = SKU
        fields = ('__all__')