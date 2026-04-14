from models import Order, DeliverySchedule


class ReminderService:
    """到期提醒服务"""

    @staticmethod
    def get_pickup_reminders():
        """获取待提货提醒（客户要求交期已过但状态非已结款/完结的订单）"""
        orders = Order.query.join(DeliverySchedule).filter(
            Order.primary_status.in_(['正常']),
            Order.secondary_status.in_(['生产中', '待提货', '部分发货']),
        ).all()
        return orders

    @staticmethod
    def get_payment_reminders():
        """获取待结款提醒"""
        orders = Order.query.filter(
            Order.primary_status.in_(['正常']),
            Order.secondary_status.in_(['待结款']),
        ).all()
        return orders
