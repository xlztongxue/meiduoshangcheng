from django.contrib.auth.models import Group
from rest_framework import serializers
class GroupSerializer(serializers.ModelSerializer):
    """用户组权限"""
    class Meta:
        model = Group
        fields = '__all__'