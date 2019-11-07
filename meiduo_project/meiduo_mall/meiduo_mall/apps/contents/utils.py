from collections import OrderedDict
from goods.models import GoodsChannel


def get_categories():
    # 准备商品分类所对应的字典
    categories = OrderedDict()
    # 查询展示商品分类
    # channels = GoodsChannel.objects.all().order_by('')
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 遍历所有频道
    for channel in channels:
        # 获取当前频道所在的组的id
        group_id = channel.group_id
        # 只有11个组所以需要判断
        if group_id not in categories:
            categories[group_id] = {
                'channels': [],
                'sub_cats': []
            }
        # 当前频道对应的一级类别
        cat1 = channel.category
        # 将cat1添加追加当前频道
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 查询二级和三级类别
        for cat2 in cat1.subs.all():
            # 给二级类别添加保存三级类别的列表
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                # 将三级类别添加到二级类别
                cat2.sub_cats.append(cat3)
            # 将二级类别添加到一级类别
            categories[group_id]['sub_cats'].append(cat2)
    return categories