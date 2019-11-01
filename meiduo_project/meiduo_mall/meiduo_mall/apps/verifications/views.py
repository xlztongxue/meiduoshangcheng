import random, logging
from django import http
from django.views import View

from verifications import constants
from django_redis import get_redis_connection
from meiduo_mall.utils.response_code import RETCODE
from celery_tasks.sms.tasks import send_sms_code
from verifications.libs.captcha.captcha import captcha


# 创建日志输出器
logger = logging.getLogger('django')


class ImageCodeView(View):
    """图形验证码"""
    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属于的用户
        :return: image/jpg
        """
        # 接受校验参数
        text, image = captcha.generate_captcha()
        # 实现主题业务逻辑，生成，保存，响应图形验证码
        redis_conn = get_redis_connection('verify_code')
        # 设置过期时间
        # redis.conn.setex(key值, 时间以秒为单位, value值)可以设置过期时间
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # 响应图形验证码
        return http.HttpResponse(image, content_type='image/jpg')


class SMSCodeView(View):
    """短信验证码"""
    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: json
        """
        # 接受参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 校验参数
        if not all([image_code_client, uuid]):
            return http.HttpResponse('缺少必传参数')
        # 实现主题业务逻辑　
        # 连接redis数据库
        redis_conn = get_redis_connection('verify_code')

        # 判断用户是否频繁发送短信验证码
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 1.提取图形验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已失效'})
        # 2.删除图形验证码
        redis_conn.delete('img_%s' % uuid)
        # 3.对比图形验证码
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码填写有误'})

        # 生成手机短信验证码：随机6位有机数字
        sms_code = '%06d' % random.randint(0, 999999)
        # 手动输出日志,记录短信验证码
        logger.info(sms_code)

        # 创建Redis管道
        pl = redis_conn.pipeline()
        # 保存手机短信验证码
        pl.setex('sms_%s' % mobile, constants.IMAGE_CODE_REDIS_EXPIRES, sms_code)
        # 保存手机短信验证码已经发送的标记
        pl.setex('send_flag_%s' % mobile, constants.IMAGE_CODE_REDIS_EXPIRES, 1)
        # 执行请求
        pl.execute()

        # 发送短信验证码
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES//60],　constants.SEND_SMS_TEMPLATE_ID)

        # 执行异步任务发短信（使用celery发送短信验证）
        # send_sms_code(mobile, sms_code) 错误写法
        send_sms_code.delay(mobile, sms_code) # 正确的语法

        # 响应短信验证码
        print("发送成功")
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '短信验证码发送成功'})


