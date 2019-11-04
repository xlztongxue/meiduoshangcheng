import logging

from django import http
from django.views import View
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage

from contents.utils import get_categories
from goods.models import GoodsCategory, SKU, GoodsVisitCount
from goods.utils import get_breadcrumb
from meiduo_mall.utils.response_code import RETCODE
from orders.models import OrderGoods

logger = logging.getLogger('django')


class GoodsCommentView(View):
    """订单商品评价信息"""

    def get(self, request, sku_id):
        # 获取被评价的订单商品信息
        order_goods_list = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True).order_by('-create_time')[:30]
        # 序列化
        comment_list = []
        for order_goods in order_goods_list:
            username = order_goods.order.user.username
            comment_list.append({
                'username': username[0] + '***' + username[-1] if order_goods.is_anonymous else username,
                'comment':order_goods.comment,
                'score':order_goods.score,
            })
        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'comment_list': comment_list})


class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request, category_id):
        """记录分类商品访问量"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('缺少必传参数')
        # 方法一 使用上海时区 LANGUAGE_CODE = 'Asia/Shanghai'

        # # 获取当天日期
        # t = timezone.localtime()
        # # 获取当天的时间字符串
        # today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)
        # # 将当天的时间字符串转成时间对象，为了跟datetime匹配
        # today_time = datetime.strptime(today_str, '%Y-%m-%d')

        # 方法二 禁用时区 USE_TZ = False 推荐使用第二种
        today_time = datetime.today()
        # 统计指定分类商品的访问量
        try:
            # 如果存在，直接获取记录的对象
            counts_data = GoodsVisitCount.objects.get(date=today_time, category=category)
        except GoodsVisitCount.DoesNotExist:
            # 如果不存在，创建记录所对应的对象
            counts_data = GoodsVisitCount()
        try:
            counts_data.category = category
            counts_data.count += 1
            counts_data.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('统计失败')
        # 响应结果
        return http.JsonResponse({'code':RETCODE.OK, 'errsmg':'OK'})


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        # 接收参数和校验参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)
        # 查询sku
        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return render(request, '404.html')
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options
        # 构造上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku':sku,
            'specs': goods_specs,
        }
        return render(request, 'detail.html', context)


class HotGoodsView(View):
    """热销排行"""
    def get(self, request, category_id):
        # 查询指定分类的SKU信息，而且必须是上架的状态
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
        # 将模型列表转字典列表，构造json数据
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url':sku.default_image.url
            })
        return http.JsonResponse({'code':RETCODE.OK, 'errmg': 'OK', 'hot_skus':hot_skus})


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        """提供商品列表页"""
        # 校验参数
        # 校验category_id的范围
        try:
            # 三级类别
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist as e:
            logger.error(e)
            return http.HttpResponseForbidden('参数category_id不存在')
        # 获取sort(排序规则)
        sort = request.GET.get('sort', 'default')
        # 根据sort选择排序字段，排序字段必须是模型类的属性
        # 按照价格
        if sort == 'price':
            sort_field = 'price'
        # 按照销量
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            # 当出现?sort = xlz sort=default
            sort = 'default'
            sort_field = 'create_time'
        # 查询商品分类
        categories = get_categories()
        # 查询面包屑导航 一级-二级-三级
        breadcrumb = get_breadcrumb(category)
        # 排序category查询sku，一查多
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)
        # 分页
        # 创建分页器
        # Paginator('要分页的记录', '每页的条数')
        paginator = Paginator(skus, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
        # 获取用户当前要看的那一页(核心)
        try:
            page_skus = paginator.page(page_num)
        except EmptyPage as e:
            logger.error(e)
            return http.HttpResponseNotFound('空的页面')
        # 获取总页数：前端需要使用
        total_page = paginator.num_pages
        # 构造上下文
        context = {
            'categories':categories, # 频道分类
            'breadcrumb':breadcrumb, # 面包屑导航
            'page_skus': page_skus, # 分页后数据
            'total_page': total_page, # 总页数
            'page_num': page_num, # 当前页码
            'sort': sort, # 排序字段
            'category': category, # 第三级分类
            'category_id':category_id # 第三级分类id
        }
        return render(request, 'list.html', context)