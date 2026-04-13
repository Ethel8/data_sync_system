from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.order_service import list_orders, get_order, complete_order, set_anomaly, refund_order

bp = Blueprint('order', __name__, url_prefix='/orders')


@bp.route('/')
def order_list():
    status = request.args.get('status')
    company_id = request.args.get('company_id', type=int)
    keyword = request.args.get('keyword')
    page = request.args.get('page', 1, type=int)
    pagination = list_orders(status=status, company_id=company_id, keyword=keyword, page=page)
    return render_template('order/list.html', pagination=pagination, filters=request.args)


@bp.route('/<int:order_id>')
def order_detail(order_id):
    order = get_order(order_id)
    logs = order.logs.order_by('created_at').all()
    return render_template('order/detail.html', order=order, logs=logs)


@bp.route('/<int:order_id>/complete', methods=['POST'])
def do_complete(order_id):
    remark = request.form.get('remark', '')
    complete_order(order_id, remark)
    flash('订单已完结入库', 'success')
    return redirect(url_for('order.order_detail', order_id=order_id))


@bp.route('/<int:order_id>/anomaly', methods=['POST'])
def do_anomaly(order_id):
    remark = request.form.get('remark', '')
    set_anomaly(order_id, remark)
    flash('订单已标记为异常', 'warning')
    return redirect(url_for('order.order_detail', order_id=order_id))


@bp.route('/<int:order_id>/refund', methods=['POST'])
def do_refund(order_id):
    remark = request.form.get('remark', '')
    refund_order(order_id, remark)
    flash('订单已标记为退单', 'info')
    return redirect(url_for('order.order_detail', order_id=order_id))
