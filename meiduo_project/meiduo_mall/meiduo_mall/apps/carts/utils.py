import base64
import pickle

from django_redis import get_redis_connection


def merge_carts_cookies_redis(request, user, response):
    """
    登录后合并cookie购物车数据到Redis
    :param request: 本次请求对象，获取cookie中的数据
    :param response: 本次响应对象，清除cookie中的数据
    :param user: 登录用户信息，获取user_id
    :return: response
    """
    # 获取cookie中的购物车
    cart_str = request.COOKIES.get('carts')
    # 判断是否有cookie购物车
    if not cart_str:
        return response
    # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
    cookie_cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
    # 准备新的容器保存合并购物车
    new_cart_dict = {}
    new_selected_add = []
    new_selected_rem = []
    # 遍历cookie中的购物车
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)
    # 合并购物车
    # 将cookie中购物车数据添加到hash
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('carts_%s' % user.id, new_cart_dict)
    # 将勾选状态同步到Redis数据库
    if new_selected_add:
        pl.sadd('selected_%s' % user.id, *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_%s' % user.id, *new_selected_rem)
    # 执行
    pl.execute()
    # 删除cookie中的carts
    response.delete_cookie('carts')
    # response是可变对象，可以不返回
    # return response