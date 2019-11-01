import logging

import base64
import json

import pickle
from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE


logger = logging.getLogger('django')

class CartsSimpleView(View):
    """商品页面右上角购物车"""
    def get(self, request):
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询Redis购物车
            redis_conn = get_redis_connection('carts')
            # 查询hash数据方法 hgetall('key')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 查询set数据方法 smembers('key')
            redis_selected = redis_conn.smembers('selected_%s' % user.id)
            # 构造数据结果跟未登录数据结果一致，为了未登录和登录展示购物车结果可以统一代码
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    "count": int(count),
                    "selected": sku_id in redis_selected  # True or False
                }
        else:
            # 用户未登录，查询cookie购物车
            # 如果用户没有登录查询cookie
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
        # 构造购物车渲染结果
        # 获取字典中所以的key, sku_id
        sku_ids = cart_dict.keys()
        # 一次性查询所有的skus再遍历
        skus = SKU.objects.filter(id__in=sku_ids)
        # # 构造简单购物车JSON数据
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url
            })
        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'cart_skus':cart_skus})


class CartsSelectAllView(View):
    """全选购物车"""
    def put(self, request):
        # 接收和校验参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)
        if selected:
            # 校验selected是bool型
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            # 获取所有key
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 获取字典中所有的key
            redis_sku_ids = redis_cart.keys()
            # 判断用户是否全选
            if selected:
                # 全选
                redis_conn.sadd('selected_%s' % user.id, *redis_sku_ids)
            else:
                # 取消全选
                redis_conn.srem('selected_%s' % user.id, *redis_sku_ids)
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 用户未登录，操作cookie购物车
            # 获取cookie中的购物车数据，并且判断是否有购物车数据
            cart_str = request.COOKIES.get('carts')
            # 构造响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                # 遍历所有的购物车记录
                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected  # True or False
                # 将字典转成将bytes类型的字典转成bytes的字符串转成字符串
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 重写购物车cookie
                response.set_cookie('carts', cookie_cart_str)
            return response


class CartsView(View):
    """购物车管理"""

    def get(self, request):
        """展示购物车"""
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 如果用户登录则查询redis数据库
            redis_conn = get_redis_connection('carts')
            # 查询hash数据方法 hgetall('key')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 查询set数据方法 smembers('key')
            redis_selected = redis_conn.smembers('selected_%s' % user.id)
            # 构造数据结果跟未登录数据结果一致，为了未登录和登录展示购物车结果可以统一代码
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    "count": int(count),
                    "selected": sku_id in redis_selected  # True or False
                }
        else:
            # 如果用户没有登录查询cookie
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
        # 构造购物车渲染结果
        # 获取字典中所以的key, sku_id
        sku_ids = cart_dict.keys()
        # 方法一
        # for sku_id in sku_ids:
        #   sku = SKU.objects.get(id=sku_id)
        # 方法二 尽量使用这种提高数据库性能
        # 一次性查询所有的skus再遍历
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * cart_dict.get(sku.id).get('count')),
            })
        context = {
            'cart_skus': cart_skus,
        }
        # 响应结果
        # 渲染购物车页面
        return render(request, 'cart.html', context)

    def post(self, request):
        """保存购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 校验参数
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 校验sku_id是否合法
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id不存在')
        # 校验count是否是数字
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count错误')
        # 判断是否勾选
        if selected:
            # 校验selected是bool型
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 如果用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 需要以增量计算的形式保存商品数据(判断商品是否在购物车中存在)
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            # 保存商品勾选状态
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()
            # 响应结果
            return http.JsonResponse({'code':RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 如果用户未登录 操作cookie购物车
            # 获取cookie中的购物车数据，并且判断是否有购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 判断当前要添加的商品在carts_dict中是否存在
            if sku_id in cart_dict:
                # 购物车商品存在,商品增量加1
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            cart_dict[sku_id]={
                'count':count,
                'selected': selected
            }
        # 将新的购物写入cookie
        response = http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK'})
        # 将字典转成将bytes类型的字典转成bytes的字符串转成字符串
        cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
        response.set_cookie('carts', cookie_cart_str)
        # 响应结果
        return response

    def put(self, request):
        """修改购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 校验参数
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 校验sku_id是否合法
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id不存在')
        # 校验count是否是数字
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count错误')
        # 判断是否勾选
        if selected:
            # 校验selected是bool型
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 如果用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 由于前端接收的是最终结果，所以覆盖写入
            pl.hset('carts_%s' % user.id, sku_id, count)
            # 修改商品勾选状态
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()
            # 响应结果
            # 创建响应对象
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
        else:
            # 如果用户未登录 操作cookie购物车
            # 获取cookie中的购物车数据，并且判断是否有购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 覆盖写入
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 创建响应对象
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            # 将新的购物写入cookie
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
            # 将字典转成将bytes类型的字典转成bytes的字符串转成字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('carts', cookie_cart_str)
            return response

    def delete(self, request):
        """删除购物车商品"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        # 校验参数
        # 校验sku_id是否合法
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id不存在')
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 如果用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 删除购物车商品记录
            pl.hdel('carts_%s' % user.id, sku_id)
            # 同步移除勾选状态
            pl.srem('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()
            return  http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 如果用户未登录 操作cookie购物车
            # 获取cookie中的购物车数据，并且判断是否有购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 构造响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            # 判断商品是否在购物车种
            if sku_id in cart_dict:
                # 删除字典指定key所对应的记录
                del cart_dict[sku_id]
                # 将字典转成将bytes类型的字典转成bytes的字符串转成字符串
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie('carts', cookie_cart_str)
            return response


