from flask import Blueprint, render_template, request, jsonify
from app import db
from models import Order, OrderLog
from services.order_status_engine import recalculate_order_status

order_bp = Blueprint('order', __name__)


@order_bp.route('/', methods=['GET'])
def list_orders():
    """订单列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    order_status = request.args.get('status', '', type=str)
    order_progress = request.args.get('progress', '', type=str)
    keyword = request.args.get('keyword', '', type=str)

    query = Order.query

    if order_status:
        query = query.filter_by(order_status=order_status)
    if order_progress:
        query = query.filter_by(order_progress=order_progress)
    if keyword:
        query = query.filter(
            db.or_(
                Order.sales_order_no.contains(keyword),
                Order.ship_to_name.contains(keyword),
                Order.fara_external_code.contains(keyword),
            )
        )

    pagination = query.order_by(Order.updated_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items

    return render_template('order/list.html', orders=orders, pagination=pagination)


@order_bp.route('/<int:order_id>', methods=['GET'])
def order_detail(order_id):
    """订单详情"""
    order = Order.query.get_or_404(order_id)
    logs = OrderLog.query.filter_by(order_id=order_id).order_by(OrderLog.created_at.desc()).all()
    return render_template('order/detail.html', order=order, logs=logs)


@order_bp.route('/<int:order_id>/status', methods=['PATCH'])
def update_status(order_id):
    """手动修改订单状态"""
    order = Order.query.get_or_404(order_id)
    data = request.get_json() or {}

    old_status = order.order_status
    old_progress = order.order_progress

    # 支持修改订单状态
    if 'order_status' in data:
        new_status = data['order_status']
        if new_status in ['正常', '异常', '退单']:
            order.order_status = new_status

    # 支持修改订单进度（异常状态变更为手动设置的）
    if 'order_progress' in data:
        new_progress = data['order_progress']
        valid_progress = ['生产中', '待提货', '部分发货', '待结款', '已结款',
                          '超时未提货', '超时未结款', '入库后退货', '开票后退货']
        if new_progress in valid_progress:
            order.order_progress = new_progress

    # 支持设置开票为"需退票"
    if 'factory_invoice_status' in data and data['factory_invoice_status'] == '需退票':
        order.factory_invoice_status = '需退票'
    if 'customer_invoice_status' in data and data['customer_invoice_status'] == '需退票':
        order.customer_invoice_status = '需退票'

    # 重算最终状态
    recalculate_order_status(order)

    # 记录日志
    log = OrderLog(
        order_id=order.id,
        action='手动修改状态',
        detail=f'订单状态: {old_status}→{order.order_status}, 进度: {old_progress}→{order.order_progress}'
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'success': True, 'order': {
        'order_status': order.order_status,
        'order_progress': order.order_progress,
        'factory_invoice_status': order.factory_invoice_status,
        'customer_invoice_status': order.customer_invoice_status,
    }})
