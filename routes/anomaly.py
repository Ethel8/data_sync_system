from flask import Blueprint, render_template
from models import Order

anomaly_bp = Blueprint('anomaly', __name__)


@anomaly_bp.route('/', methods=['GET'])
def list_anomalies():
    """异常订单列表"""
    orders = Order.query.filter_by(order_status='异常').order_by(Order.updated_at.desc()).all()
    return render_template('anomaly/list.html', orders=orders)
