import json
import logging

from datetime import datetime
from django import http
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.views import View
from django.shortcuts import render
from django_redis import get_redis_connection
from decimal import Decimal

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from orders.models import OrderInfo, OrderGoods
from users.models import Address
from meiduo_mall.utils.views import LoginRequestJSONMixin, LoginRequiredMixin

logger = logging.getLogger('django')



class OrderCommentView(LoginRequiredMixin, View):
    """订单商品评价"""

    def get(self, request):
        """展示商品评价页面"""
        # 接收参数
        order_id = request.GET.get('order_id')
        # 校验参数
        try:
            OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseNotFound('订单不存在')

        # 查询订单中未被评价的商品信息
        try:
            uncomment_goods = OrderGoods.objects.filter(order_id=order_id, is_commented=False)
        except Exception:
            return http.HttpResponseServerError('订单商品信息出错')

        # 构造待评价商品数据
        uncomment_goods_list = []
        for goods in uncomment_goods:
            uncomment_goods_list.append({
                'order_id':goods.order.order_id,
                'sku_id':goods.sku.id,
                'name':goods.sku.name,
                'price':str(goods.price),
                'default_image_url':goods.sku.default_image.url,
                'comment':goods.comment,
                'score':goods.score,
                'is_anonymous':str(goods.is_anonymous),
            })

        # 渲染模板
        context = {
            'uncomment_goods_list': uncomment_goods_list
        }
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        """评价订单商品"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        score = json_dict.get('score')
        comment = json_dict.get('comment')
        is_anonymous = json_dict.get('is_anonymous')
        # 校验参数
        if not all([order_id, sku_id, score, comment]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            OrderInfo.objects.filter(order_id=order_id, user=request.user,
                                     status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('参数order_id错误')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        if is_anonymous:
            if not isinstance(is_anonymous, bool):
                return http.HttpResponseForbidden('参数is_anonymous错误')

        # 保存订单商品评价数据
        OrderGoods.objects.filter(order_id=order_id, sku_id=sku_id, is_commented=False).update(
            comment=comment,
            score=score,
            is_anonymous=is_anonymous,
            is_commented=True
        )

        # 累计评论数据
        sku.comments += 1
        sku.save()
        sku.spu.comments += 1
        sku.spu.save()

        # 如果所有订单商品都已评价，则修改订单状态为已完成
        if OrderGoods.objects.filter(order_id=order_id, is_commented=False).count() == 0:
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '评价成功'})


class UserOrderInfoView(LoginRequiredMixin, View):
    """我的订单"""

    def get(self, request, page_num):
        """用户中心提供我的订单页面"""
        user = request.user
        # 查询订单
        orders = user.orderinfo_set.all().order_by('-create_time')
        # 遍历订单
        for order in orders:
            # 绑定订单状态
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]
            # 绑定支付方式
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            # 创建列表装订单商品
            order.sku_list = []
            # 查询订单商品
            order_goods = order.skus.all()
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price*sku.count
                order.sku_list.append(sku)
        # 分页
        try:
            paginator = Paginator(orders, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
            # 获取用户当前要看的那一页(核心)
            page_orders = paginator.page(int(page_num))
            total_page = paginator.num_pages
        except EmptyPage as e:
            logger.error(e)
            return http.HttpResponseNotFound('订单不存在')
        # 获取总页数：前端需要使用
        total_page = paginator.num_pages
        context = {
            "page_orders": page_orders,
            'total_page': total_page,
            'page_num': int(page_num),
        }
        return render(request, "user_center_order.html", context)


class OrderSuccessView(LoginRequiredMixin, View):
    """展示订单页面"""
    def get(self, request):
        """展示订单页面"""
        # 接收参数
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')
        context = {
            'order_id':order_id,
            'payment_amount':payment_amount,
            'pay_method':pay_method
        }
        return render(request, 'order_success.html', context)


class OrderCommitView(LoginRequestJSONMixin, View):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断address_id是否存在
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数支付方式错误')
        # 保存订单基本信息(1)
        # 1.明显的开启一次事务
        try:
            with transaction.atomic():
                # 获取登录由用户
                user = request.user
                # 生成订单编号：时间+user_id
                #  timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
                #  order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id) 时区被禁
                order_id =  datetime.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
                # 支付状态
                # status = 'UNPAID' if pay_method == 'ALIPAY' else 'UNSEND',  # 需要判断
                status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] \
                    if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] \
                    else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                order = OrderInfo.objects.create(
                    order_id= order_id,
                    user = user,
                    address = address,
                    total_count = 0,
                    total_amount = Decimal(0.00),
                    freight = Decimal(10.00),
                    pay_method = pay_method,
                    status = status
                )
                print(datetime.now())
                # 保存订单商品信息(多)
                # 查询购物车订单中的勾选的商品数据
                redis_conn = get_redis_connection('carts')
                # 查询购物车中所有的数据
                redis_cart = redis_conn.hgetall('carts_%s' % user.id)
                # 查询购物车中被勾选的商品id
                redis_selected = redis_conn.smembers('selected_%s' % user.id)
                # 构造购物车中被勾选的字典
                new_cart_dict = {}
                for sku_id in redis_selected:
                    new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])
                # 读取勾选的购物车商品信息
                sku_ids = new_cart_dict.keys()
                # 遍历购物车商品信息
                for sku_id in sku_ids:
                    # 每个商品都有一次下单的机会直到库存不足或者商品下单成功
                    while True:
                        # 查询商品和库存信息时，不能出现缓存，所以不能使用filter，只能用get
                        sku = SKU.objects.get(id=sku_id)
                        # 获取原始的库存数量和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        # 获取要提交订单的商品的数量
                        sku_count = new_cart_dict[sku_id]
                        # 判断商品数量是否大于库存，如果大于库存,响应'库存不足'

                        # raise FError('库存不足')
                        if sku_count > sku.stock:
                            raise Exception('库存不足')

                        # 如果库存满足需求，则sku减库存，加销量
                        # 解决下单高并发问题
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,sales=new_sales)
                        if result == 0:
                            continue
                        OrderGoods.objects.create(
                            order = order,
                            sku = sku,
                            count = sku_count,
                            price = sku.price
                        )
                        # 累加订单商品的数量到订单基本信息表
                        order.total_count += sku_count
                        order.total_amount += sku.price*sku_count
                        # 下单成功，记得break
                        break
                # 再加最后的运费
                order.total_amount += order.freight
                order.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg': str(e)})

        # 下单成功清除购物车勾选的内容
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *redis_selected)
        pl.srem('selected_%s' % user.id, *redis_selected)
        pl.execute()
        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'order_id': order_id})


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""
    def get(self, request):
        """提供订单结算页面"""
        # 查询登录用户没有被删除的用户收货地址
        user = request.user
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Exception as e:
            logger(e)
            # 没有地址可以去编辑地址
            address = None
        redis_conn = get_redis_connection('carts')
        # 查询购物车中所有的数据
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        # 查询购物车中被勾选的商品id
        redis_selected = redis_conn.smembers('selected_%s' % user.id)
        # 构造购物车中被勾选的字典
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])
        # 遍历new_cart_dict，取出去sku_id和count
        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        # 遍历skus补充count(数量)和amount(小计)
        # 累加
        total_count = Decimal(0.00) # Decimal('0')
        total_amount = Decimal(0.00)
        for sku in skus:
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price*sku.count # Decimal类型

            # 累加数量和金额
            total_amount += sku.count
            total_amount += sku.amount
        # 指定默认的邮费
        freight = Decimal(10.00)
        # 构造上下文
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
        }
        return render(request, 'place_order.html', context)
