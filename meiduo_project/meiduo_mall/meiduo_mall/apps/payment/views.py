import os
from alipay import AliPay
from django import http
from django.conf import settings
from django.shortcuts import render
from django.views import View

from meiduo_mall.utils.response_code import RETCODE
from orders.models import OrderInfo
from payment.models import Payment


class PaymentStatusView(View):
    """保存支付的订单状态"""
    def get(self, requset):
        """"""
        # 获取所有的查询字符串参数，将查询字符串参数的类型转成标准的字典类型
        query_dict = requset.GET
        data = query_dict.dict()

        # 从查询字符参数中提取并移除sign不能参与验证
        sign = data.pop('sign')

        # 创建SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        # 使用SDK对象，调用验证通知接口函数，得到验证结果
        success = alipay.verify(data, sign)
        # 如果验证通过，需要支付宝状态进行处理
        if success:
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')
            # 保存支付订单(有就更新，没有就创建)
            Payment.objects.update_or_create(
                order_id = order_id,
                defaults={'trade_id' : trade_id}
            )
            # 修改订单状态，有待支付变为待评价
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])

            # 构造响应数据trade_id
            context= {
                'trade_id': trade_id
            }
            return render(requset, 'pay_success.html', context)
        # 如果验证未通过
        else:
            return http.HttpResponseForbidden('非法请求')


class PaymentView(View):
    """对戒支付宝的接口"""
    def get(self, request, order_id):
        """
        :param request:
        :param order_id: 当前要支付的id
        :return: JSON
        """
        user = request.user
        # 校验order_id
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单不存在')

        # 创建对接支付宝的SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # SDK对象对接支付宝的接口，得到登陆地址
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id, # 订单编号
            total_amount=str(order.total_amount), # 订单支付金额
            subject="美多商城%s" % order_id, # 订单标题
            return_url=settings.ALIPAY_RETURN_URL, # 同步通知的回调地址
        )

        # 拼接完整的支付宝登录页面
        # 响应登录支付宝连接
        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})

