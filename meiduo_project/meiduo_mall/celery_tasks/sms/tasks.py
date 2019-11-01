# 3.2定义任务
import logging

from celery import Task
from celery_tasks.sms.yuntongxun.ccp_sms import CCP
from celery_tasks.sms import constants
from celery_tasks.main import celery_app

logger = logging.getLogger('django')

# 判断是否执行任务成功
class MyTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        # 注意自己定义的任务
        print('调用异步任务完成')
        print('retval', retval)
        print('task_id', task_id)
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('调用异步任务失败')
        print('retval', exc)
        print('task_id', task_id)
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs)


# 使用装饰器装饰异步任务，保证celery识别任务
@celery_app.task(bind=True, name='send_sms_code', retry_backoff=3)
def send_sms_code(self, mobile, sms_code):
    """
    发送短信验证码的异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 成功:0,失败：-1
    """
    try:
        send_ret = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
        return send_ret
    except Exception as e:
        logger.error(e)
        # 有异常重试三次
        raise self.retry(exc=e, max_retries=3)

