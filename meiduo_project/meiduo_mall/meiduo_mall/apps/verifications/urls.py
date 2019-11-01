from django.conf.urls import url
from . import views

urlpatterns = [
    # 图形验证码之生成图形验证码　接口
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    # 短信验证之生成短信验证码 接口
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/', views.SMSCodeView.as_view()),
]
