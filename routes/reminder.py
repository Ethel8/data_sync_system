from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template
from models import Order, DeliverySchedule
from services.order_status_engine import _safe_date

reminder_bp = Blueprint('reminder', __name__)


@reminder_bp.route('/', methods=['GET'])
def index():
    """到期提醒"""
    today = date.today()

    # 提醒提货：订单进度=="待提货" 且 今天 == 交期表的订单评审交期
    pickup_reminders = []
    pending_pickup_orders = Order.query.filter_by(order_progress='待提货', order_status='正常').all()
    for order in pending_pickup_orders:
        ds = DeliverySchedule.query.filter_by(
            sales_order_no=order.sales_order_no,
            fara_external_code=order.fara_external_code,
            order_quantity=order.order_quantity
        ).first()
        if ds:
            review_date = _safe_date(ds.order_review_date)
            if review_date and today == review_date:
                pickup_reminders.append({
                    'order': order,
                    'review_date': review_date,
                })

    # 提醒结款：订单进度=="待结款" 且 今天 == 发货日期 + 1个月
    payment_reminders = []
    pending_payment_orders = Order.query.filter_by(order_progress='待结款', order_status='正常').all()
    for order in pending_payment_orders:
        ship_d = _safe_date(order.ship_date)
        if ship_d:
            one_month_later = ship_d + relativedelta(months=1)
            if today == one_month_later:
                payment_reminders.append({
                    'order': order,
                    'ship_date': ship_d,
                    'payment_due_date': one_month_later,
                })

    # 提醒公司开票：订单进度=="已结款" 且 订单状态=="正常"（非完结）且 公司开票!="已开票"
    factory_invoice_reminders = Order.query.filter(
        Order.order_progress == '已结款',
        Order.order_status == '正常',
        Order.factory_invoice_status != '已开票'
    ).all()

    # 提醒客户开票：同上但检查客户开票
    customer_invoice_reminders = Order.query.filter(
        Order.order_progress == '已结款',
        Order.order_status == '正常',
        Order.customer_invoice_status != '已开票'
    ).all()

    return render_template('reminder/index.html',
                           pickup_reminders=pickup_reminders,
                           payment_reminders=payment_reminders,
                           factory_invoice_reminders=factory_invoice_reminders,
                           customer_invoice_reminders=customer_invoice_reminders)
