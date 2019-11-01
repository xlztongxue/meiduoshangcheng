from django.conf.urls import url, include
from . import views
urlpatterns = [
    # 提高QQ登录扫码页面
    url('^qq/login/', views.QQAuthURLView.as_view()),
    # 处理QQ登录回调
    url('^oauth_callback/', views.QQAuthUserView.as_view()),
]
