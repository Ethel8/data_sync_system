from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Order, DeliverySchedule, OrderLog
from services.order_service import OrderService
from app import db

order_bp = Blueprint('order', __name__)


@order_bp.route('/')
def list_orders():
    """订单查询"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # 筛选条件
    primary_status = request.args.get('primary_status', '')
    secondary_status = request.args.get('secondary_status', '')
    keyword = request.args.get('keyword', '')
    search_field = request.args.get('search_field', 'sales_order_no')

    query = Order.query.join(DeliverySchedule)

    if primary_status:
        query = query.filter(Order.primary_status == primary_status)
    if secondary_status:
        query = query.filter(Order.secondary_status == secondary_status)
    if keyword:
        if search_field == 'sales_order_no':
            query = query.filter(DeliverySchedule.sales_order_no.contains(keyword))
        elif search_field == 'customer_name':
            query = query.filter(DeliverySchedule.customer_name.contains(keyword))

    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('order/list.html', orders=orders,
                           primary_status=primary_status,
                           secondary_status=secondary_status,
                           keyword=keyword, search_field=search_field)


@order_bp.route('/<int:order_id>')
def detail(order_id):
    """订单详情"""
    order = Order.query.get_or_404(order_id)
    logs = OrderLog.query.filter_by(order_id=order_id).order_by(OrderLog.changed_at.desc()).all()
    return render_template('order/detail.html', order=order, logs=logs)


@order_bp.route('/create', methods=['GET', 'POST'])
def create():
    """订单创建 - 基于交期表"""
    if request.method == 'POST':
        ds_id = request.form.get('delivery_schedule_id', type=int)
        order, error = OrderService.create_order(ds_id)
        if error:
            flash(error, 'danger')
        else:
            flash('订单创建成功', 'success')
            return redirect(url_for('order.detail', order_id=order.id))

    # 获取未创建订单的交期表记录
    existing_ds_ids = {o.delivery_schedule_id for o in Order.query.all() if o.delivery_schedule_id}
    schedules = DeliverySchedule.query.filter(
        ~DeliverySchedule.id.in_(existing_ds_ids) if existing_ds_ids else True
    ).order_by(DeliverySchedule.create_date.desc()).limit(100).all()

    return render_template('order/create.html', schedules=schedules)


@order_bp.route('/<int:order_id>/update_status', methods=['POST'])
def update_status(order_id):
    """更新订单状态"""
    primary_status = request.form.get('primary_status')
    secondary_status = request.form.get('secondary_status')
    remark = request.form.get('remark', '')

    order, error = OrderService.update_status(order_id, primary_status, secondary_status, remark)
    if error:
        flash(error, 'danger')
    else:
        flash('状态更新成功', 'success')
    return redirect(url_for('order.detail', order_id=order_id))
