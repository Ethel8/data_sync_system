"""到期提醒服务"""
from datetime import date, timedelta
from config import REMINDER_PICKUP_DAYS_BEFORE, REMINDER_PAYMENT_DAYS_BEFORE


def check_pickup_reminders():
    """检查需要提醒提货的订单"""
    from models.order import Order
    today = date.today()
    target = today + timedelta(days=REMINDER_PICKUP_DAYS_BEFORE)
    orders = Order.query.filter(
        Order.status == OrderStatus.NORMAL,
        Order.delivery_date <= target,
        Order.delivery_date >= today,
    ).all()
    return orders


def check_payment_reminders():
    """检查需要提醒结款的订单"""
    from models.order import Order, OrderStatus
    today = date.today()
    target = today + timedelta(days=REMINDER_PAYMENT_DAYS_BEFORE)
    orders = Order.query.filter(
        Order.status == OrderStatus.NORMAL,
        Order.payment_due_date <= target,
        Order.payment_due_date >= today,
    ).all()
    return orders


def get_all_reminders():
    """汇总所有待提醒事项"""
    return {
        'pickup': check_pickup_reminders(),
        'payment': check_payment_reminders(),
    }
