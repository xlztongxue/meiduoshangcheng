from django.conf.urls import url
from . import views

urlpatterns = [
    # 结算订单
    url(r'orders/settlement/$',views.OrderSettlementView.as_view(), name='settlement'),
    # 提交订单
    url(r'orders/commit/$',views.OrderCommitView.as_view()),
    # 展示订单
    url(r'orders/success/$',views.OrderSuccessView.as_view()),
    # 用户中心展示订单
    url(r'orders/info/(?P<page_num>\d+)/', views.UserOrderInfoView.as_view(),name='info'),
    # 用户评价信息
    url(r'orders/comment/', views.OrderCommentView.as_view(), name='comment')
]