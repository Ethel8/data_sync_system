from flask import Blueprint, render_template, request, jsonify
from services.payment_service import get_payment_overview, process_payment

payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/', methods=['GET'])
def index():
    """结款界面"""
    overview = get_payment_overview()
    return render_template('payment/index.html', overview=overview)


@payment_bp.route('/submit', methods=['POST'])
def submit_payment():
    """提交结款"""
    data = request.get_json() or {}

    ship_to_name = data.get('ship_to_name', '').strip()
    amount = data.get('amount', 0)

    if not ship_to_name:
        return jsonify({'success': False, 'error': '请选择客户'}), 400

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': '金额格式错误'}), 400

    success, message, settled_orders = process_payment(ship_to_name, amount)

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'settled_count': len(settled_orders),
        })
    else:
        return jsonify({'success': False, 'error': message}), 400
