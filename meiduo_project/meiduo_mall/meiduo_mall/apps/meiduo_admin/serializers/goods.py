from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from goods.models import SPUSpecification


class SpecsSerialzier(ModelSerializer):
    """规格序列化器"""

    # 指定关联外键返回形式
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = SPUSpecification
        fields = ('__all__')
