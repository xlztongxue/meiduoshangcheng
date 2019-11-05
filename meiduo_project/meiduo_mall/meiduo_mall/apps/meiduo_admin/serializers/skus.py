from django.db import transaction
from rest_framework import serializers

from goods.models import SKU, SKUSpecification
from celery_tasks.static_file.tasks import generate_detail_html


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """SKU具体规格序列化器"""
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()
    class Meta:
        model = SKUSpecification
        fields = ('spec_id', 'option_id')

class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    # 获取 specificationoption_set{}.spec_id
    specs = SKUSpecificationSerializer(many=True)
    class Meta:
        model = SKU
        fields = '__all__'
    def create(self, validated_data):
        try:
            # 开启事务
            with transaction.atomic():
                specs = validated_data.pop('specs')
                # 保存sku表
                sku = super().create(validated_data)
                # 保存sku具体规格表
                for spec in specs:
                    spec['sku'] = sku
                    SKUSpecification.objects.create(**spec)
        except Exception:
            raise serializers.ValidationError('保存失败')
        # 生成详情页的静态页面
        generate_detail_html.delay(sku.id)
        return sku
