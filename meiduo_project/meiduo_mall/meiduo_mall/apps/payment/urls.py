from django.conf.urls import url
from . import views
urlpatterns=[
    # 对接支付宝
    url(r'payment/(?P<order_id>\d+)/', views.PaymentView.as_view()),
    # 保存订单状态
    url(r'payment/status/', views.PaymentStatusView.as_view()),
]