from app import db
from models import Order, OrderLog, DeliverySchedule


class OrderService:
    """订单业务服务"""

    # 一级状态 -> 合法的二级状态
    VALID_SECONDARY_STATUSES = {
        '正常': [
            '生产中', '待提货', '部分发货', '待结款', '已结款',
            '工厂未开票', '工厂部分开票', '工厂已开票', '工厂需退票',
            '法拉未开票', '法拉部分开票', '法拉已开票', '法拉需退票',
        ],
        '异常': ['超时未提货', '超时未结款', '入库后退货', '开票后退货'],
        '完结': [],
        '退单': [],
    }

    @staticmethod
    def create_order(delivery_schedule_id):
        """基于交期表创建订单"""
        ds = DeliverySchedule.query.get(delivery_schedule_id)
        if not ds:
            return None, '交期表记录不存在'
        order = Order(
            delivery_schedule_id=delivery_schedule_id,
            primary_status='正常',
            secondary_status='生产中',
        )
        db.session.add(order)
        db.session.commit()
        OrderService._log(order.id, None, '正常/生产中', '创建订单')
        return order, None

    @staticmethod
    def update_status(order_id, primary_status, secondary_status, remark=''):
        """更新订单状态"""
        order = Order.query.get(order_id)
        if not order:
            return None, '订单不存在'

        old_status = f'{order.primary_status}/{order.secondary_status}'
        new_status = f'{primary_status}/{secondary_status}'

        if primary_status in OrderService.VALID_SECONDARY_STATUSES:
            if secondary_status and secondary_status not in OrderService.VALID_SECONDARY_STATUSES[primary_status]:
                return None, f'无效的二级状态: {secondary_status}，一级状态为{primary_status}时允许: {OrderService.VALID_SECONDARY_STATUSES[primary_status]}'

        order.primary_status = primary_status
        order.secondary_status = secondary_status
        db.session.commit()
        OrderService._log(order.id, old_status, new_status, remark)
        return order, None

    @staticmethod
    def _log(order_id, from_status, to_status, remark=''):
        log = OrderLog(
            order_id=order_id,
            from_status=from_status,
            to_status=to_status,
            remark=remark,
        )
        db.session.add(log)
        db.session.commit()
