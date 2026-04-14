from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.anomaly_detection import AnomalyDetectionService

anomaly_bp = Blueprint('anomaly', __name__)


@anomaly_bp.route('/')
def list_anomalies():
    anomalies = AnomalyDetectionService.get_anomaly_orders()
    return render_template('anomaly/list.html', anomalies=anomalies)


@anomaly_bp.route('/<int:order_id>/restore', methods=['POST'])
def restore(order_id):
    secondary_status = request.form.get('secondary_status', '生产中')
    remark = request.form.get('remark', '恢复为正常')
    order, error = AnomalyDetectionService.restore_normal(order_id, secondary_status, remark)
    if error:
        flash(error, 'danger')
    else:
        flash('订单已恢复为正常状态', 'success')
    return redirect(url_for('anomaly.list_anomalies'))


@anomaly_bp.route('/<int:order_id>/set_returned', methods=['POST'])
def set_returned(order_id):
    remark = request.form.get('remark', '标记为退单')
    order, error = AnomalyDetectionService.set_returned(order_id, remark)
    if error:
        flash(error, 'danger')
    else:
        flash('订单已标记为退单', 'success')
    return redirect(url_for('anomaly.list_anomalies'))
