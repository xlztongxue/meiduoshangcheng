from datetime import datetime
from django.db.models import Q
from rest_framework import serializers
from meiduo_admin.utils.repayload import jwt_data_hander
from users.models import User


class AdminAuthSerializer(serializers.ModelSerializer):
    """管理员序列化器类"""
    username = serializers.CharField(label='用户名')
    token = serializers.CharField(label='JWT Token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'token')

        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
            },
            'username':{
                'max_length': 20,
                'min_length': 8,
            }
        }

    def validate(self, attrs):
        # 获取username和password
        username = attrs['username']
        password = attrs['password']

        # 进行用户名和密码校验,添加邮箱验证
        user = User.objects.filter(Q(username=username) | Q(email=username), is_staff=True).first()
        # 校验密码
        if not user or not user.check_password(password):
            raise serializers.ValidationError('用户名或密码错误')
            # 给attrs中添加user属性，保存登录用户
        attrs['user'] = user

        return attrs

    def create(self, validated_data):
        # 获取登录用户user
        user = validated_data['user']
        # 设置最新登录时间
        user.last_login = datetime.now()
        user.save()
        # 服务器生成jwt token, 保存当前用户的身份信息
        user = jwt_data_hander(user)

        return user