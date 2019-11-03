from django.conf.urls import url
from meiduo_admin.views import users, statistical


urlpatterns = [
    # 美多后台用户登录：meiduo_admin/authorizations
    url(r'^authorizations/$', users.AdminAuthorizeView.as_view()),
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


]

