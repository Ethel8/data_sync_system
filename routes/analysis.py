from flask import Blueprint, render_template
from app import db
from models import Order, DeliverySchedule

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/reconciliation', methods=['GET'])
def reconciliation():
    """对账表 - 完结订单"""
    orders = Order.query.filter_by(order_status='完结').order_by(Order.updated_at.desc()).all()

    result = []
    for order in orders:
        # 从交期表获取客户物料代码
        ds = DeliverySchedule.query.filter_by(
            sales_order_no=order.sales_order_no,
            fara_external_code=order.fara_external_code,
            order_quantity=order.order_quantity
        ).first()

        shipped_qty = order.shipped_quantity or 0
        purchase_price = order.purchase_price_excl_tax or 0
        sell_price_total = order.customer_payable_incl_tax or 0
        buy_price_total = purchase_price * shipped_qty

        item = {
            'order': order,
            'customer_material_code': ds.customer_material_code if ds else '',
            'shipped_quantity': shipped_qty,
            'ship_date': order.ship_date,
            'purchase_price_excl_tax': purchase_price,
            'buy_price_total': round(buy_price_total, 2),
            'sell_price_total': round(sell_price_total, 2),
        }

        if shipped_qty > 0:
            item['sell_price_unit'] = round(sell_price_total / shipped_qty, 2)
        else:
            item['sell_price_unit'] = 0

        if buy_price_total > 0:
            item['profit_rate'] = round(sell_price_total / buy_price_total - 1, 4)
            item['profit'] = round(sell_price_total - buy_price_total, 2)
        else:
            item['profit_rate'] = 0
            item['profit'] = 0

        result.append(item)

    return render_template('analysis/reconciliation.html', items=result)


@analysis_bp.route('/arrears', methods=['GET'])
def arrears():
    """欠款表 - 各客户待结款总额"""
    # 按 ship_to_name 分组，统计待结款订单的客户应付含税金额总和
    results = db.session.query(
        Order.ship_to_name,
        db.func.sum(Order.customer_payable_incl_tax).label('total_arrears'),
        db.func.count(Order.id).label('order_count')
    ).filter(
        Order.order_progress == '待结款'
    ).group_by(
        Order.ship_to_name
    ).all()

    items = []
    for row in results:
        items.append({
            'ship_to_name': row.ship_to_name,
            'total_arrears': round(row.total_arrears or 0, 2),
            'order_count': row.order_count,
        })

    return render_template('analysis/arrears.html', items=items)
