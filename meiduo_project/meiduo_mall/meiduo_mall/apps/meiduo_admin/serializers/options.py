from rest_framework import serializers
from goods.models import SpecificationOption, SPUSpecification


class OptionSerializer(serializers.ModelSerializer):
    """商品频道组序列化器"""
    # 关联对象嵌套序列化
    spec = serializers.StringRelatedField(read_only=True)
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        exclude = ('create_time', 'update_time')


class SpuSerializer(serializers.ModelSerializer):
    """商品SPU规格序列化器"""
    spu = serializers.StringRelatedField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SPUSpecification
        exclude = ('create_time', 'update_time')

    def get_name(self, obj):
        return f'{obj.spu} {obj.name}'

