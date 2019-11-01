from django.conf.urls import url
from . import views

urlpatterns = [
    # 商品列表页
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/', views.ListView.as_view(), name='list'),
    # 热销排行
    url(r'^hot/(?P<category_id>\d+)/', views.HotGoodsView.as_view()),
    # 商品详情页
    url(r'^detail/(?P<sku_id>\d+)/', views.DetailView.as_view(), name='detail'),
    # 统计商品浏览量
    url(r'^detail/visit/(?P<category_id>\d+)/', views.DetailVisitView.as_view()),
    # 产看评价信息
    url(r'^comments/(?P<sku_id>\d+)//', views.GoodsCommentView.as_view()),
]