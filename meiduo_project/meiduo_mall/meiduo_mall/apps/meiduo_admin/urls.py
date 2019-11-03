from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from meiduo_admin.views import users, statistical, goods

urlpatterns = [
    # 美多后台用户登录：meiduo_admin/authorizations
    url(r'^authorizations/$', obtain_jwt_token),
    # 用户总数统计：GETmeiduo_admin/statistical/total_count/
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
    # 日增用户统计：GET /meiduo_admin/statistical/day_increment/
    url(r'^statistical/day_increment/$', statistical.UserDayIncrementView.as_view()),
    # 日活跃用户：GET /meiduo_admin/statistical/day_active/
    url(r'^statistical/day_active/$', statistical.UserDayActiveView.as_view()),
    # 日下单用户：GET /meiduo_admin/statistical/day_orders/
    url(r'statistical/day_orders/$', statistical.UserDayOrdersView.as_view()),
    # 月增用户统计：GET /meiduo_admin/statistical/month_increment/
    url(r'statistical/month_increment/$', statistical.UserMonthIncrementView.as_view()),
    # 日分类增用户统计：GET /meiduo_admin/statistical/goods_day_views/
    url(r'statistical/goods_day_views/$', statistical.GoodsDayView.as_view()),
    # 用户管理：GET /meiduo_admin/users/?page=1&pagesize=10&keyword
    url(r'^users/$', users.UserInfoView.as_view()),

]

# 商品规格信息自动生成路由
router = DefaultRouter()
# 生成路由
router.register('goods/specs/', goods.SpecsViewSet, base_name='specs')
# 导入到原有路由列表中
urlpatterns += router.urls





