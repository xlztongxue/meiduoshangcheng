"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 全文检索haystack路由自己写死了不能改变
    url(r'^search/', include('haystack.urls')),
    # users　注册页面
    url(r'^', include('users.urls', namespace='users')),
    # contents 首页广告
    url(r'^', include('contents.urls', namespace='contents')),
    # 图形验证
    url(r'^', include('verifications.urls')),
    # QQ第三方认证登录
    url(r'^', include('oauth.urls')),
    # 收货地址
    url(r'^', include('areas.urls')),
    # 商品展示
    url(r'^', include('goods.urls', namespace='goods')),
    # 购物车
    url(r'^', include('carts.urls', namespace='carts')),
    # 订单
    url(r'^', include('orders.urls', namespace='orders')),
    # 支付宝支付
    url(r'^', include('payment.urls', namespace='payment')),
    # 用户后台管理
    url('^meiduo_admin/', include('meiduo_admin.urls')),
]
