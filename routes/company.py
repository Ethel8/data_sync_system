from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Company
from app import db

company_bp = Blueprint('company', __name__)


@company_bp.route('/')
def list_companies():
    keyword = request.args.get('keyword', '')
    query = Company.query
    if keyword:
        query = query.filter(
            db.or_(
                Company.company_name.contains(keyword),
                Company.manager.contains(keyword),
                Company.contact_person.contains(keyword),
            )
        )
    companies = query.order_by(Company.company_name).all()
    return render_template('company/list.html', companies=companies, keyword=keyword)


@company_bp.route('/<int:company_id>/edit', methods=['POST'])
def edit(company_id):
    company = Company.query.get_or_404(company_id)
    company.company_name = request.form.get('company_name', company.company_name)
    company.shipping_address = request.form.get('shipping_address', company.shipping_address)
    company.manager = request.form.get('manager', company.manager)
    company.contact_person = request.form.get('contact_person', company.contact_person)
    company.online_contact = request.form.get('online_contact', company.online_contact)
    company.phone = request.form.get('phone', company.phone)
    db.session.commit()
    flash('公司信息更新成功', 'success')
    return redirect(url_for('company.list_companies'))
