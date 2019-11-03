import json
import logging, re

import time
from django.db import DatabaseError
from django.shortcuts import render, redirect, reverse
from django import http
from django.views import View
from django.http import HttpResponseForbidden
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout

from carts.utils import merge_carts_cookies_redis
from goods.models import SKU
from meiduo_mall.utils.views import LoginRequestJSONMixin
from meiduo_mall.utils.response_code import RETCODE
from users.models import User, Address
from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_verfy_email_url, check_verify_token
from . import constants

# Create your models here.

# 创建日志器
logger = logging.getLogger('django')


class ChangePasswordView(LoginRequiredMixin, View):
    """修改密码"""

    def get(self, request):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """实现修改密码"""
        # 接收参数
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')
        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return HttpResponseForbidden("缺少必传参数")
        # 验证旧密码是否填写正确
        if not request.user.check_password(old_password):
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        # 判断新密码是否是8-20个字符
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', new_password):
            return HttpResponseForbidden("请输入8-20个字符的密码")
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', new_password2):
            return HttpResponseForbidden("请输入8-20个字符的密码")
        # 判断两次输入的密码是否一致
        if new_password != new_password2:
            return HttpResponseForbidden("再次输入的密码不一致")
        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except DatabaseError as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})
        # 清理状态保持信息
        logout(request)
        response = redirect(reverse('users:login'))
        # 响应密码修改结果，重定向到登陆页面
        return response


class UserBrowseHistory(LoginRequestJSONMixin, View):
    """用户浏览记录"""

    def get(self, request):
        """查询用户浏览记录"""
        # 接收参数
        # 获取用户登录信息
        user = request.user
        # 创建连接对象
        redis_conn = get_redis_connection('history')
        # 取出列表数据(核心代码)
        #  ZREVRANK
        # 方法一
        # sku_ids = redis_conn.lrange('history_%s' % user.id, 0, -1) # (0, 4)

        # 方法二
        sku_ids = redis_conn.zrevrange('history_%s' % user.id, 0, 4)
        # 将模型转字典
        # 查询sku_id
        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})

    def post(self, request):
        """保存用户浏览记录"""
        # 接收参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        sku_id = json_dict.get('sku_id')
        # 校验参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        # 保存sku_id到redis数据库
        redis_conn = get_redis_connection('history')
        user = request.user
        pl = redis_conn.pipeline()
        # 方法一 用列表存储
        # 去重
        # pl.lrem('history_%s' % user.id, 0 , sku_id)
        # # 再保存，最近浏览的商品在最前面
        # pl.lpush('history_%s' % user.id, sku_id)
        # # 最后截取
        # pl.ltrim('history_%s' % user.id, 0, 4)

        # 方法二 用有序集合存储

        pl.zadd('history_%s' % user.id, **{sku_id: time.time()})

        # 执行结果
        pl.execute()
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class UpdateTitleAddressView(LoginRequestJSONMixin, View):
    """设置地址标题"""

    def put(self, request, address_id):
        """设置地址标题"""
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        # 校验参数
        if not title:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '缺少标题'})

        # 查询当前要更新地址标题
        try:
            address = Address.objects.get(id=address_id, user=request.user)
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改标题失败'})

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改标题成功'})


class DefaultAddressView(LoginRequestJSONMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """设置默认地址"""
        # 设置地址为默认地址
        # 接收参数,查询地址
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


class UpdateDestoryAdressView(LoginRequestJSONMixin, View):
    """更新地址"""

    def put(self, request, address_id):
        """
        更新地址
        :param request:
        :param address_id:修改删除
        :return:
        """
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id, user=request.user).update(
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})
        # 响应新的地址信息给前端渲染
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        # 实现指定地址的逻辑删除
        try:
            address = Address.objects.get(id=address_id, user=request.user)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


class CreateAddressView(LoginRequestJSONMixin, View):
    """新增地址"""

    def post(self, request):
        """实现新增地址逻辑"""
        # 判断判断是否超过地址上限：最多20个
        # # Address.objects.filter(user=request.user).count()
        # 高级查询 一查多
        count = request.user.addresses.count()
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超出添加地址的上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        json_dict['user'] = request.user
        try:
            address = Address.objects.create(**json_dict)
            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 响应新增地址 将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 面向对象的思想，把地址传给前端
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})
        # return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': json_dict})


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        # 获取用户地址列表
        login_user = request.user

        # 使用当前登录用户和is_deleted=False作为条件查询
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        # 将查询的地址模型列表转化为字典：因为vue.js不认识模型类，只有Djanjo和jinja2引擎认识
        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)
        # 构造上下文
        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,

        }

        return render(request, 'user_center_site.html', context)


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """
        提供用户注册页面
        :param request: 请求对象
        :return: 注册页面
        """
        return render(request, 'register.html')


    def post(self, request):
        """
        实现用户注册逻辑
        :param request: 请求对象
        :return: 注册结果
        """
        # 接受参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        # 校验参数:前后端的校验需要分开，避免恶意用户越过前端发请求，
        # 要保证后端的安全，前后端的校验逻辑相同
        # 判断参数是否齐全
        # all(列表)回去校验列表中的元素是否为空，只要有一个为空，返回false
        if not all([username, password, password2, mobile, sms_code_client, allow]):
            return HttpResponseForbidden("缺少必传参数")
        # 判断用户名是否是5-20个字符重复
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否是8-20个字符
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return HttpResponseForbidden("请输入8-20个字符的密码")
        # 判断两次输入的密码是否一致
        if password != password2:
            return HttpResponseForbidden("再次输入的密码不一致")
        # 判断手机号码是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden("请输入正确的手机号码")

        # 判断短信验证码是否输入正确
        try:
            redis_conn = get_redis_connection('verify_code')
            sms_code_server = redis_conn.get('sms_%s' % mobile)
        except Exception as e:
            logger.error(e)
        if sms_code_server is None:
            return render(request, 'register.html', {'register_errmsg': '短信验证码已经失效'})
        if sms_code_server.decode() != sms_code_client:
            return render(request, 'register.html', {'register_errmsg': '短信验证码输入有误'})

        # 判断用户是否勾选了协议
        if allow != "on":
            return HttpResponseForbidden("请勾选用户协议")

        # 保存注册数据，是注册业务的核心
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError as e:
            logger.error(e)
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 状态保持
        login(request, user)

        # 响应结果：重定向到首页
        # 为了实现在首页的右上角展示用户名信息，我们需要将用户名缓存到cookie中
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # 若用户登录成功，合并cookie中的购物车
        merge_carts_cookies_redis(request=request, user=user, response=response)
        # 响应结果
        return response


class LoginView(View):
    """用户登录"""

    def get(self, request):
        """提供用户登录页面"""
        return render(request, 'login.html')

    def post(self, request):
        """实现用户登录逻辑"""
        # 接受参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符重复
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否是8-20个字符
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return HttpResponseForbidden("请输入8-20个字符的密码")
        # 认证用户
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'acount_errmsg': '帐号或密码错误'})
        # 状态保持
        login(request, user)
        # 使用remenber确定状态保持周期（实现记住登录）
        if remembered != 'on':
            # 没有记住登录：状态保持在浏览器会话结束后就销毁，单位是秒
            request.session.set_expiry(0)
        else:
            # 记录状态保持周期为两周：默认是两周
            request.session.set_expiry(None)
        response = redirect(reverse('contents:index'))
        # 先取出next
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        # 为了实现在首页的右上角展示用户名信息，我们需要将用户名缓存到cookie中
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # 若用户登录成功，合并cookie中的购物车
        merge_carts_cookies_redis(request=request, user=user, response=response)
        # 响应结果
        return response


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        """实现用户退出登录逻辑"""
        # 清除用户状态保持状态
        logout(request)
        # 删除cookie用户名信息
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')
        # 响应结果
        return response


class EmailView(LoginRequestJSONMixin, View):
    """添加邮箱"""

    def put(self, request):
        """
        :param request：请求对象
        :return:添加邮箱结果
        """
        # 接收参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')

        # 校验参数
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')
        # 将用户传入的邮箱保存到用户数据库的email字段中
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})
        # 生成邮箱激活链接
        verify_url = generate_verfy_email_url(request.user)

        # 异步发送验证邮件
        # send_verify_email(email, verify_url) # 错误写法
        send_verify_email.delay(email, verify_url)  # 记得调用delay

        # 响应添加邮箱结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):
        # 接收参数
        token = request.GET.get('token')

        # 校验参数
        if not token:
            return http.HttpResponseForbidden('缺少token')

        # 从token中提取用户信息use_id
        user = check_verify_token(token)
        if not user:
            return http.HttpResponseBadRequest('无效的token')

        # 将用户的active_email的字段设置为1
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮箱失败')

        # 响应结果：重定向到用户用心
        return redirect(reverse('users:info'))


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供个人信息界面"""
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return render(request, 'user_center_info.html', context)


class UsernameCountView(View):
    """判断用户是否重名"""

    def get(self, request, username):
        """
        :param username: 用户名
        :return: JSON
        """
        # 接受和校验参数
        # 实现主体业务，使用username查询对应的记录的条数
        # filter()返回满足结果的字符集
        count = User.objects.filter(username=username).count()

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobilesCountView(View):
    """判断手机号是否重复"""

    def get(self, request, mobile):
        """
        :param mobile: 手机号
        :return: JSON
        """
        # 接受和校验参数
        # 实现主体业务，使用username查询对应的记录的条数
        count = User.objects.filter(mobile=mobile).count()
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


