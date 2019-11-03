import calendar
import datetime

# 判断时间是否正确
from django.db.models import Count
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay

from users.models import User


def get_last_month_day(date):
    year, month, day = date.year, date.month, date.day
    if month == 1:
        year = year - 1
        month = 12
    else:
        month = month - 1
    weekday, max_day = calendar.monthrange(year, month)
    if day > max_day:
        day = max_day
    return datetime.date(year, month, day)

# 生成时间迭代器
def get_all_date(start_day, end_day):
    return_day = start_day
    while return_day <= end_day:
        yield return_day
        return_day += datetime.timedelta(days=1)


def get_return_day_count_list(start_time, end_time):
    # 查询出不为0的所有数据
    day_counts = User.objects.filter(
        date_joined__gte=start_time, date_joined__lt=end_time).annotate(
        year=ExtractYear('date_joined'), month=ExtractMonth('date_joined'), date=ExtractDay('date_joined')
    ).values('year', 'month', 'date').annotate(nums=Count(0))

    # 构造字典
    day_counts_dict = {datetime.date(day['year'], day['month'], day['date']): day['nums'] for day in day_counts}
    return_daty_dict = {i: 0 for i in get_all_date(start_time, end_time)}

    # 合并字典
    return_daty_dict.update(day_counts_dict)

    # 构造返回结果
    return_day_count_list = [{
        'count': count,
        'date': date
    } for date, count in return_daty_dict.items()]
    return return_day_count_list
