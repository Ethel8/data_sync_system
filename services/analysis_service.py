"""统计分析服务：对账表、欠款表、利润率"""
from db.database import db
from models.order import Order, OrderStatus
from sqlalchemy import func


def get_reconciliation():
    """对账表：已结单数据汇总"""
    orders = Order.query.filter_by(status=OrderStatus.COMPLETED).all()
    data = []
    for o in orders:
        data.append({
            'order_no': o.order_no,
            'company_name': o.company.name if o.company else '',
            'product_name': o.product_name,
            'quantity': o.quantity,
            'unit_price': o.unit_price,
            'total_amount': o.total_amount,
            'completed_at': o.completed_at,
        })

    total_amount = sum(d['total_amount'] for d in data if d['total_amount'])
    return {
        'orders': data,
        'total_amount': total_amount,
        'count': len(data),
    }


def get_arrears():
    """欠款表：异常/未结款订单"""
    orders = Order.query.filter(
        Order.status.in_([OrderStatus.NORMAL, OrderStatus.ANOMALY])
    ).all()
    data = []
    for o in orders:
        data.append({
            'order_no': o.order_no,
            'company_name': o.company.name if o.company else '',
            'total_amount': o.total_amount,
            'status': o.get_status_label(),
            'payment_due_date': o.payment_due_date,
        })

    total_arrears = sum(d['total_amount'] for d in data if d['total_amount'])
    return {
        'orders': data,
        'total_arrears': total_arrears,
        'count': len(data),
    }


def get_profit_summary():
    """利润率分析"""
    # TODO: 根据实际成本数据实现
    return {'message': '待实现：需补充成本数据'}
