# 静态页面和用户无关，是开发者在项目之前生成
import os
from collections import OrderedDict
from django.conf import settings
from django.template import loader
from contents.models import ContentCategory
from contents.utils import get_categories


def generate_static_index_html():
    """静态化首页"""
    # 查询并展示商品分类
    # 查询并展示商品分类
    categories = get_categories()

    # 查询广告数据
    # 查询所有广告的类别
    contents = OrderedDict()
    context_categories = ContentCategory.objects.all()
    for content_category in context_categories:
        # 查询出为下架的广告
        contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')

        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents
        }
    # 渲染数据
    # 先获取模板文件
    template = loader.get_template('index.html')
    # 再使用上下文渲染文件
    html_text = template.render(context)
    # 准备文件路径，放在静态文件下
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    # 将模板文件写入静态路径
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
