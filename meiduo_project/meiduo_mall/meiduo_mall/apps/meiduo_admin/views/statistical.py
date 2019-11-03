from datetime import datetime, date, timedelta
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import GoodsVisitCount
from meiduo_admin.serializers.statistical import GoodsVisitSerializer
from meiduo_admin.utils.gettime import get_last_month_day, get_return_day_count_list
from meiduo_admin.utils.repayload import response_date
from users.models import User

# 用户总数统计视图
class UserTotalCountView(APIView):
    # 用户登录验证
    permission_classes = [IsAdminUser]
    """
        获取网站总用户数:
        1. 获取网站总用户数量
        2. 返回应答
    """
    def get(self, request):
        # 1.获取当前网站用户总数
        now_data = datetime.now()
        count = User.objects.count()
        # 2.返回应答
        response_data = response_date(now_data, count)
        return Response(response_data)

# 日增用户统计
class UserDayIncrementView(APIView):
    # 用户登录验证
    permission_classes = [IsAdminUser]
    """
        获取网站总用户数:
        1. 获取网站总用户数量
        2. 返回应答
    """
    def get(self, request):
        # 1.获取当前网站用户总数
        now_data = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(date_joined__gte=now_data).count()
        # 2.返回应答
        response_data = response_date(now_data, count)
        return Response(response_data)

# 日活跃用户统计
class UserDayActiveView(APIView):
    # 用户登录验证
    permission_classes = [IsAdminUser]
    """
        获取网站总用户数:
        1. 获取网站总用户数量
        2. 返回应答
    """
    def get(self, request):
        # 1.获取当前网站用户总数
        now_data = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(last_login__gte=now_data).count()
        # 2.返回应答
        response_data = response_date(now_data, count)
        return Response(response_data)

# 下单用户统计
class UserDayOrdersView(APIView):
    # 用户登录验证
    permission_classes = [IsAdminUser]
    """
        获取网站总用户数:
        1. 获取网站总用户数量
        2. 返回应答
    """
    def get(self, request):
        # 1.获取当前网站用户总数
        now_data = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # distinct(去重)
        count = User.objects.filter(orderinfo__create_time__gte=now_data).distinct().count()
        # 2.返回应答
        response_data = response_date(now_data, count)
        return Response(response_data)

# 当月增用户统计
class UserMonthIncrementView(APIView):
    # 用户登录验证
    permission_classes = [IsAdminUser]
    """
        获取当月每日新增用户数据:
        1. 获取当月每日新增用户数据
        2. 返回应答
    """
    # 1. 获取当月每日新增用户数据
    def get(self, request):
        # 现在时间
        now_day = date.today() + timedelta(days=1)
        last_month_day = get_last_month_day(now_day)
        data_list = get_return_day_count_list(last_month_day, now_day)
        return Response(data_list)

# 日分类商品访问量
class GoodsDayView(APIView):
    # 用户登录验证
    permission_classes = [IsAdminUser]
    """
        获取当日分类商品访问量：
        1. 查询获取当日分类商品访问量
        2. 将查询数据序列化并返回
    """
    def get(self, request):
        # 1.查询获取当日分类商品访问量
        now_data = datetime.now().date()
        good_visit = GoodsVisitCount.objects.filter(date=now_data)

        # 2.将查询数据序列化并返回
        # 注意many = True别忘了
        serializer = GoodsVisitSerializer(good_visit, many=True)
        return Response(serializer.data)
