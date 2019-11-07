from rest_framework import serializers

from goods.models import SPU


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化器"""
    # 指定外键
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()
    brand_id = serializers.IntegerField()
    brand = serializers.StringRelatedField()
    class Meta:
        model = SPU
        fields = '__all__'