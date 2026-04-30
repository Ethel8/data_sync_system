from flask import Blueprint, render_template, request, jsonify
from app import db
from models import Company

company_bp = Blueprint('company', __name__)


@company_bp.route('/', methods=['GET'])
def list_companies():
    """客户明细列表"""
    companies = Company.query.order_by(Company.ship_to_name).all()
    return render_template('company/list.html', companies=companies)


@company_bp.route('/', methods=['POST'])
def create_or_update_company():
    """新增或更新客户"""
    data = request.get_json() or {}

    if not data.get('ship_to_name'):
        return jsonify({'success': False, 'error': '送达方名称不能为空'}), 400

    existing = Company.query.filter_by(ship_to_name=data['ship_to_name']).first()
    if existing:
        for key in ['delivery_address', 'manager', 'contact_person', 'online_contact', 'phone']:
            if key in data:
                setattr(existing, key, data[key])
        db.session.add(existing)
        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功'})
    else:
        company = Company(
            ship_to_name=data['ship_to_name'],
            delivery_address=data.get('delivery_address', ''),
            manager=data.get('manager', ''),
            contact_person=data.get('contact_person', ''),
            online_contact=data.get('online_contact', ''),
            phone=data.get('phone', ''),
        )
        db.session.add(company)
        db.session.commit()

        # 更新订单主表负责人
        from services.order_status_engine import update_all_orders_manager
        update_all_orders_manager()
        db.session.commit()

        return jsonify({'success': True, 'message': '创建成功'})
