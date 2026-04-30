from app import db
from models import Company, Order, OrderLog
from services.order_status_engine import recalculate_order_status


def get_payment_overview():
    """
    获取结款概览：所有送达方及其已结款未开票额度。
    Returns: list of dict {ship_to_name, uninvoiced_paid, pending_orders_count, total_arrears}
    """
    companies = Company.query.order_by(Company.ship_to_name).all()
    result = []
    for c in companies:
        # 该客户待结款订单数量和总欠款
        pending_orders = Order.query.filter_by(
            ship_to_name=c.ship_to_name,
            order_progress='待结款'
        ).order_by(Order.create_date).all()

        total_arrears = sum(
            _safe_float(o.customer_payable_incl_tax) for o in pending_orders
        )

        result.append({
            'company': c,
            'ship_to_name': c.ship_to_name,
            'uninvoiced_paid': _safe_float(c.uninvoiced_paid),
            'pending_orders': pending_orders,
            'pending_orders_count': len(pending_orders),
            'total_arrears': round(total_arrears, 2),
        })
    return result


def process_payment(ship_to_name, amount):
    """
    处理结款：将金额累计入已结款未开票额度，然后自动按创建日期顺序扣款。

    Args:
        ship_to_name: 送达方名称
        amount: 结款金额（正数）

    Returns:
        (success, message, settled_orders)
    """
    if amount <= 0:
        return False, '结款金额必须大于0', []

    company = Company.query.filter_by(ship_to_name=ship_to_name).first()
    if not company:
        return False, f'未找到客户: {ship_to_name}', []

    # 累计入已结款未开票额度
    company.uninvoiced_paid = _safe_float(company.uninvoiced_paid) + amount
    remaining = company.uninvoiced_paid

    # 获取该客户所有待结款订单，按创建日期排序
    pending_orders = Order.query.filter_by(
        ship_to_name=ship_to_name,
        order_progress='待结款'
    ).order_by(Order.create_date).all()

    settled_orders = []
    for order in pending_orders:
        if remaining <= 0:
            break

        payable = _safe_float(order.customer_payable_incl_tax)
        if payable <= 0:
            continue

        if remaining >= payable:
            # 额度满足，扣款
            remaining -= payable
            order.order_progress = '已结款'

            log = OrderLog(
                order_id=order.id,
                action='自动结款',
                detail=f'结款金额 {payable}，订单标记为已结款'
            )
            db.session.add(log)
            settled_orders.append({
                'order': order,
                'amount': payable,
            })

            # 重算订单状态
            recalculate_order_status(order)

    # 更新剩余额度
    company.uninvoiced_paid = remaining

    db.session.commit()

    settled_total = sum(s['amount'] for s in settled_orders)
    message = f'结款成功：累计 {amount}，自动完结 {len(settled_orders)} 笔订单（共 {settled_total}），剩余额度 {round(remaining, 2)}'
    return True, message, settled_orders


def _safe_float(val):
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0
