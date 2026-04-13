from db.database import db
from models.order import Order, OrderStatus
from models.log import OperationLog
from datetime import datetime


def create_order(**kwargs):
    """创建订单"""
    order = Order(**kwargs)
    order.status = OrderStatus.NORMAL
    db.session.add(order)
    db.session.flush()

    _add_log(order.id, 'create', new_value=OrderStatus.NORMAL, remark='订单创建')
    db.session.commit()
    return order


def get_order(order_id):
    return Order.query.get_or_404(order_id)


def list_orders(status=None, company_id=None, keyword=None, page=1, per_page=20):
    """订单列表查询，支持筛选和分页"""
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    if company_id:
        query = query.filter_by(company_id=company_id)
    if keyword:
        query = query.filter(
            Order.order_no.contains(keyword) |
            Order.customer_material_code.contains(keyword) |
            Order.falah_code.contains(keyword)
        )
    # 关联公司名称搜索
    if keyword:
        from models.company import Company
        company_ids = [c.id for c in Company.query.filter(Company.name.contains(keyword)).all()]
        if company_ids:
            query = query.filter((Order.company_id.in_(company_ids)) if not hasattr(query, '_joinpoint') else Order.company_id.in_(company_ids))
    query = query.order_by(Order.created_at.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)


def update_status(order_id, new_status, remark=''):
    """更新订单状态"""
    order = get_order(order_id)
    old_status = order.status
    order.status = new_status
    order.updated_at = datetime.now()

    if new_status == OrderStatus.COMPLETED:
        order.completed_at = datetime.now()

    _add_log(order.id, 'update_status', old_value=old_status, new_value=new_status, remark=remark)
    db.session.commit()
    return order


def complete_order(order_id, remark=''):
    return update_status(order_id, OrderStatus.COMPLETED, remark or '订单完结入库')


def set_anomaly(order_id, remark=''):
    return update_status(order_id, OrderStatus.ANOMALY, remark or '订单异常')


def refund_order(order_id, remark=''):
    return update_status(order_id, OrderStatus.REFUNDED, remark or '订单退单')


def _add_log(order_id, action, old_value=None, new_value=None, remark=''):
    log = OperationLog(
        order_id=order_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        remark=remark,
    )
    db.session.add(log)
