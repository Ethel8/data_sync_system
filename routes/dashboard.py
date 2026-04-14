from flask import Blueprint, render_template
from models import Order, DeliverySchedule

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    total_orders = Order.query.count()
    normal_orders = Order.query.filter_by(primary_status='正常').count()
    anomaly_orders = Order.query.filter_by(primary_status='异常').count()
    completed_orders = Order.query.filter_by(primary_status='完结').count()
    returned_orders = Order.query.filter_by(primary_status='退单').count()
    delivery_count = DeliverySchedule.query.count()

    stats = {
        'total_orders': total_orders,
        'normal_orders': normal_orders,
        'anomaly_orders': anomaly_orders,
        'completed_orders': completed_orders,
        'returned_orders': returned_orders,
        'delivery_count': delivery_count,
    }
    return render_template('dashboard.html', stats=stats)
