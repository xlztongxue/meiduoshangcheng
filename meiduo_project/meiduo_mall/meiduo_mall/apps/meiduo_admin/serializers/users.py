from datetime import datetime
from django.db.models import Q
from rest_framework import serializers
from meiduo_admin.utils.repayload import jwt_data_hander
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器类"""
    class Meta:
        model=User
        fields=('id', 'username', 'mobile', 'email')
