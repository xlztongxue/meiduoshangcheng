# 开发环境的配置文件

"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os, sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(BASE_DIR)
# 查看导包路径

# print(sys.path)

# 追加导包路径
# sys.path.insert(0, '/home/python/Desktop/project/meiduo_project/meiduo_mall/meiduo_mall/apps')
# 高级添加
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(b_qp+p!)a0fidmdss1+a#nmdi3g37l94t+sy4ycv3=r25%fc)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 全文检索
    'haystack',
    # 注册用户模块
    'users.apps.UsersConfig',
    # 注册首页广告模块
    'contents.apps.ContentsConfig',
    # 注册验证图形码 可以不注册，需要迁移和模板的才需要注册
    'verifications.apps.VerificationsConfig',
    # 注册第三方登录
    'oauth.apps.OauthConfig',
    # 注册三级联动
    'areas.apps.AreasConfig',
    # 注册商品模块
    'goods.apps.GoodsConfig',
    # 订单
    'orders.apps.OrdersConfig',
    # 支付宝支付
    'payment.apps.PaymentConfig',
    # 把美多后台当作子应用注册到项目当中
    'meiduo_admin.apps.MeiduoAdminConfig',
    # 注册前端框架模块
    'rest_framework',
    # 注册定时任务
    'django_crontab',
    # 跨域模块
    'corsheaders'
]

MIDDLEWARE = [
    # 注意：跨域问题中间件添加到中间件的第一个
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 注册中间件 判断cookie信息
    # 'users.middleware.username_cookie_middleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        # 配置jinjia2模板引擎
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        # 配置模板文件加载路径
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 补充Jinja2模板引擎环境
            'environment': 'meiduo_mall.utils.jinja2_env.jinja2_environment',
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    'default': { # 主机
            'ENGINE': 'django.db.backends.mysql', # 数据库引擎
            'HOST': '192.168.152.12', # 数据库主机
            'PORT': 3306, # 数据库端口
            'USER': 'root', # 数据库用户名
            'PASSWORD': '123456', # 数据库用户密码
            'NAME': 'meiduo' # 数据库名字
    },
    'slave': { # 从机
                'ENGINE': 'django.db.backends.mysql', # 数据库引擎
                'HOST': '127.0.0.1', # 数据库从机
                'PORT': 3307, # 数据库端口
                'USER': 'root', # 数据库用户名
                'PASSWORD': '123456', # 数据库用户密码
                'NAME': 'meiduo' # 数据库名字
        }
}

# 配置redis数据库
# 分库处理
CACHES = {
    # 默认
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/０",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    # session
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    # 验证码储存
    "verify_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    # 浏览记录存储
    "history": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    # 购物车存储
    "carts": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
# 配置静态文件加载路径
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# 配置工程日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

# 指定本项目用户模型类
AUTH_USER_MODEL = 'users.User'

# 指定自定义的用户认证后端
AUTHENTICATION_BACKENDS = ['meiduo_mall.utils.authenticate.UsernameMobileBackend']

# 判断用户是否登录未登录
LOGIN_URL = '/login/'

# QQ登录参数
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

# 生产环境配置邮箱服务器
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # 指定邮件后端
# EMAIL_HOST = 'smtp.163.com' # 发邮件主机
# EMAIL_PORT = 25 # 发邮件端口
# EMAIL_HOST_USER = 'hmmeiduo@163.com' # 授权的邮箱
# EMAIL_HOST_PASSWORD = 'hmmeiduo123' # 邮箱授权时获得的密码，非注册登录密码
# EMAIL_FROM = '美多商城<hmmeiduo@163.com>' # 发件人抬头

# 开发测试邮箱配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # 指定邮件后端
EMAIL_FROM = '美多商城<hmmeiduo@163.com>' # 发件人抬头

# 邮箱验证链接
EMAIL_VERIFT_URL = 'http://www.meiduo.site:8000/email/verification/'


# 指定自定义的Django文件存储类
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.fdfs_storage.FastDFSStorage'

# FastDFS相关参数
FDFS_BASE_URL = 'http://192.168.152.12:8888/'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        # Elasticsearch服务器ip地址，端口号固定为9200
        'URL': 'http://192.168.152.12:9200/',
        # Elasticsearch建立的索引库的名称
        'INDEX_NAME': 'meiduo_mall',
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Haystack 分页时每页记录条数
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5


# 支付宝SDK配置参数
ALIPAY_APPID = '2016101200666299'
ALIPAY_DEBUG = True
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/'

# 定时器配置
CRONJOBS = [
    # 每1分钟生成一次首页静态文件
    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> ' + os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.log'))
]

# 指定中文编码格式
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'


# 配置数据库读写分离路由
DATABASE_ROUTERS = ['meiduo_mall.utils.db_router.MasterSlaveDBRouter']


REST_FRAMEWORK = {
    # 指定DRF框架的异常处理函数
    'EXCEPTION_HANDLER': 'meiduo_admin.utils.exceptions.exception_handler',

    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 引入JWT认证机制，当客户端将jwt token传递给服务器之后
        # 此认证机制会自动校验jwt token的有效性，无效会直接返回401(未认证错误)
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    # 全局分页类设置,指定分页器
    'DEFAULT_PAGINATION_CLASS': 'meiduo_admin.utils.pagination.PageNum',
}

JWT_AUTH = {
    # 设置生成jwt token的有效时间
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 重写指定结果返回方法
    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'meiduo_admin.utils.repayload.jwt_response_payload_handler',
}


# CORS跨域请求设置白名单
# 允许哪些路由跨域访问
CORS_ORIGIN_WHITELIST = (
    # 备注：允许源地址`http://127.0.0.0.1:8080`向当前API服务器发起跨域请求
    '127.0.0.1:8080',
    '192.168.152.12:8000',
    'www.meiduo.site:8000',
    # 'api.meiduo.site:8000',
)
# 允许携带cookie
CORS_ALLOW_CREDENTIALS = True


FASTDES_PATH = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')

