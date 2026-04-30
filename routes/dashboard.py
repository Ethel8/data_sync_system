from flask import Blueprint, render_template
from models import Order

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/', methods=['GET'])
def index():
    """首页仪表盘"""
    total_orders = Order.query.count()
    normal_orders = Order.query.filter_by(order_status='正常').count()
    anomaly_orders = Order.query.filter_by(order_status='异常').count()
    completed_orders = Order.query.filter_by(order_status='完结').count()
    refunded_orders = Order.query.filter_by(order_status='退单').count()

    # 待处理提醒
    pending_pickup = Order.query.filter_by(order_progress='待提货', order_status='正常').count()
    pending_payment = Order.query.filter_by(order_progress='待结款', order_status='正常').count()

    return render_template('dashboard.html',
                           total_orders=total_orders,
                           normal_orders=normal_orders,
                           anomaly_orders=anomaly_orders,
                           completed_orders=completed_orders,
                           refunded_orders=refunded_orders,
                           pending_pickup=pending_pickup,
                           pending_payment=pending_payment)
