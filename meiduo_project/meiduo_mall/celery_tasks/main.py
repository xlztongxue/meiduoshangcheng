# 1.celery入口文件
# from celery import Celery
#
#
# # 2.创建Celery实例
# celery_app = Celery('meiduo')
# # 3.加载配置
# celery_app.config_from_object('celery_tasks.config')
# # 4.注册任务
# celery_app.autodiscover_tasks(['celery_tasks.sms'])


# celery启动文件
from celery import Celery



# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 创建celery实例
celery_app = Celery('meiduo')

# 加载celery配置
celery_app.config_from_object('celery_tasks.config')

# 自动注册celery任务
# celery_app.autodiscover_tasks(['celery_tasks.sms'])
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
