from jinja2 import Environment
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage


def jinja2_environment(**options):
    """jinjia2环境"""
    # 创建环境对象
    env = Environment(**options)
    # 自定义语法：{{static("静态文件相对路径")}}　　{{url("路由的命名空间")}}
    env.globals.update({
        # 获取静态文件的前缀
        'static': staticfiles_storage.url,
        # 反向解析
        'url': reverse,
    })
    # 返回环境对象
    return env

