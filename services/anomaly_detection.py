from models import Order


class AnomalyDetectionService:
    """异常状态检测与变更"""

    @staticmethod
    def set_anomaly(order_id, secondary_status, remark=''):
        """将订单设为异常状态"""
        valid = ['超时未提货', '超时未结款', '入库后退货', '开票后退货']
        if secondary_status not in valid:
            return None, f'无效的异常类型: {secondary_status}'
        from services.order_service import OrderService
        return OrderService.update_status(order_id, '异常', secondary_status, remark)

    @staticmethod
    def restore_normal(order_id, secondary_status, remark=''):
        """将异常订单恢复为正常"""
        from services.order_service import OrderService
        return OrderService.update_status(order_id, '正常', secondary_status, remark)

    @staticmethod
    def set_returned(order_id, remark=''):
        """标记为退单"""
        from services.order_service import OrderService
        return OrderService.update_status(order_id, '退单', '', remark)

    @staticmethod
    def get_anomaly_orders():
        """获取所有异常订单"""
        return Order.query.filter(Order.primary_status == '异常').all()
