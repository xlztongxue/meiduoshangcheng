import re
from rest_framework import serializers
from users.models import User

# 用户登录序列化器
class UserSerializer(serializers.ModelSerializer):
    """用户序列化器类"""
    class Meta:
        model=User
        fields=('id', 'username', 'mobile', 'email','password')

        extra_kwargs = {
                    'username': {
                        'min_length': 5,
                        'max_length': 20,
                        'error_messages': {
                            'min_length': '用户名最小长度为5',
                            'max_length': '用户名最大长度为20'
                        }
                    },
                    'password': {
                        'write_only': True,
                        'min_length': 8,
                        'max_length': 20,
                        'error_messages': {
                            'min_length': '密码最小长度为8',
                            'max_length': '密码最大长度为20'
                        }
                    }
                }

    def validate_mobile(self, value):
        """手机号格式，手机号是否注册"""
        # 手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')

        # 手机号是否注册
        res = User.objects.filter(mobile=value).count()

        if res > 0:
            raise serializers.ValidationError('手机号已注册')

        return value

    def create(self, validated_data):
        """创建并保存新用户数据"""
        # 密码加密
        # # 方法一
        # user = super().create(validated_data)
        # user.set_password(validated_data['password'])
        # user.save()
        # 方法二
        user = User.objects.create_user(**validated_data)
        return user