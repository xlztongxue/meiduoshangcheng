from collections import OrderedDict
from django.shortcuts import render
from django.views import View

from contents.utils import get_categories
from contents.models import ContentCategory

# Create your views here.


class IndexView(View):
    """首页广告"""
    def get(self, request):
        """提供首页广告"""
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
                'contents':contents
            }
        return render(request, 'index.html', context)
