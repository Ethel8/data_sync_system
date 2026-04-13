"""异常检测与状态变更"""
from db.database import db
from models.order import Order, OrderStatus
from services.order_service import set_anomaly, update_status, _add_log
from datetime import datetime


def detect_overdue_pickup():
    """检测超时未取货的订单，标记为异常"""
    from config import REMINDER_PICKUP_DAYS_BEFORE
    # TODO: 根据业务规则实现
    return []


def detect_unpaid_orders():
    """检测尾款拖延的订单"""
    # TODO: 根据业务规则实现
    return []


def resolve_anomaly(order_id, remark=''):
    """异常修正 → 转回正常 → 封存入库"""
    update_status(order_id, OrderStatus.NORMAL, remark='异常修正，恢复正常')
    return update_status(order_id, OrderStatus.COMPLETED, remark='修正后封存入库')
