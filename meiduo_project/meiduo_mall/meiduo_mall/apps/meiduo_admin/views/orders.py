from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from meiduo_admin.serializers.orders import OrderDetailSerializer, OrderListSerializer, OrderStatusSerializer
from orders.models import OrderInfo


class OrderViewSet(ReadOnlyModelViewSet):
    """权限管理"""
    # 用户登录
    permission_classes = [IsAdminUser]
    # 1.指定查询集
    queryset = OrderInfo.objects.all().order_by('order_id')
    # 2.指定序列化器
    def get_serializer_class(self):
        """返回视图所使用的序列化器类"""
        if self.action == 'list':
            return OrderListSerializer
        else:
            return OrderDetailSerializer

    # 重写获取查询集数据的方法
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if not keyword:
            return self.queryset
        else:
            return self.queryset.filter(Q(order_id=keyword) |
                                              Q(skus__sku__name__contains=keyword))

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        """修改订单状态"""
        # 1. 校验订单是否有效
        order = self.get_object()

        # 2. 获取订单状态status并校验(status必传，status是否合法)
        serializer = OrderStatusSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)

        # 3. 修改并保存订单的状态
        serializer.save()

        # 4. 返回应答
        return Response(serializer.data)