from rest_framework import serializers

from goods.models import SKUImage, SKU
from celery_tasks.static_file.tasks import generate_detail_html


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
        # 方式一
        # instance = super().create(validated_data)
        # 方式二
        # 调用ModelSerializer中的create方法
        instance = super(SkuImageSerialzier, self).create(validated_data)
        sku = SKU.objects.get(id=validated_data['sku'].id)
        # 设置其默认图片
        if not sku.default_image:
            sku.default_image = instance.image
            sku.save()
        generate_detail_html.delay(instance.sku.id)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        generate_detail_html.delay(instance.sku.id)
        return instance


