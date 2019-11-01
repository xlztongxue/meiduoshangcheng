
def get_breadcrumb(category):
    """
    获取面包屑导航
    :param category: 类别对象：一级-二级-三级
    :return: 一级，返回一级；二级，返回一级+二级，三级：返回一级+二级+三级
    """
    breadcrumb = {
        'cat1': '',
        'cat2': '',
        'cat3': '',
    }
    # 说明category第一级
    if category.parent == None:
        breadcrumb['cat1'] = category
    # 说明category是第三级
    elif category.subs.count() == 0:
        cat2 = category.parent
        breadcrumb['cat1'] = cat2.parent
        breadcrumb['cat2'] = cat2
        breadcrumb['cat3'] = category
    # 说明category是第二级
    else:
        breadcrumb['cat1'] = category.parent
        breadcrumb['cat2'] = category
    return breadcrumb