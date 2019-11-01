from django.conf.urls import url
from . import views

urlpatterns = [
    # 用户注册接口设计
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # 用户名重复注册接口设计
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    # 手机号重复注册接口设计
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobilesCountView.as_view()),
    # 用户登录接口设计
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    # 用户退出登录
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # 用户中心
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    # 用户添加邮箱
    url(r'^emails/$', views.EmailView.as_view(), name='email'),
    # 用户修改密码
    url(r'^changepassword/$', views.ChangePasswordView.as_view(), name='pass'),
    # 验证邮箱
    url(r'^email/verification/$', views.VerifyEmailView.as_view(), name='verifemail'),
    # 收货地址
    url(r'^addresses/$', views.AddressView.as_view(), name='address'),
    # 新增收货地址
    url(r'^addresses/create/$', views.CreateAddressView.as_view(), name='address_create'),
    # 修改更新地址
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestoryAdressView.as_view(), name='address_update'),
    # 设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name='address_default'),
    # 修改标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view(), name='address_title'),
    # 用户浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),
]
