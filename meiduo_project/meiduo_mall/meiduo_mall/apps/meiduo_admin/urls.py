from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from meiduo_admin.views import users, statistical, specs, channels, images, options, skus, permissions, groups

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
    # 用户管理规格搜索路由表
    url(r'goods/simple/$', specs.SpecsViewSet.as_view({'get': 'simple'})),
    # 用户管理图片表搜素路由
    url(r'skus/simple/$', images.ImagesViewSet.as_view({'get': 'simple'})),
    # 用户频道组名搜索
    url(r'goods/channel_types/$', channels.ChannelsViewSet.as_view({'get': 'get_channel_types'})),
    # 用户分类ID搜索
    url(r'goods/categories/$', channels.ChannelsViewSet.as_view({'get': 'get_first_categories'})),
    # 用户规格选项搜索
    url(r'goods/specs/simple/$', options.OptionsViewSet.as_view({'get': 'simple'})),
    # 查询规格信息
    url(r'^goods/(?P<pk>\d+)/specs/$', skus.SkusViewSet.as_view({'get': 'specs'})),
    # 查询权限类型信息
    url(r'^permission/content_types/$', permissions.PermissionViewSet.as_view({'get': 'content_type'})),
    # 查询用户权限信息
    url(r'^permission/simple/$', groups.GroupViewSet.as_view({'get': 'simple'})),



]

# 自动生成路由
router = DefaultRouter()
# 生成路由
# 商品规格信息
router.register('goods/specs', specs.SpecsViewSet, base_name='specs')
# 图片表管理
router.register('skus/images', images.ImagesViewSet, base_name='image')
# 商品频道管理
router.register('goods/channels', channels.ChannelsViewSet, base_name='channels')
# 规格选项管理
router.register('specs/options', options.OptionsViewSet, base_name='options')
# SKU表管理
router.register('skus', skus.SkusViewSet, base_name='skus')
# 权限管理permission/content_types
router.register('permission/perms', permissions.PermissionViewSet , base_name='perms')
# 用户组管理
router.register('permission/groups', groups.GroupViewSet, base_name='groups')
# 导入到原有路由列表中
urlpatterns += router.urls





