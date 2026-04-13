from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.database import db
from models.company import Company

bp = Blueprint('company', __name__, url_prefix='/companies')


@bp.route('/')
def company_list():
    companies = Company.query.order_by(Company.name).all()
    return render_template('company/list.html', companies=companies)


@bp.route('/add', methods=['POST'])
def add_company():
    name = request.form.get('name')
    if not name:
        flash('公司名称不能为空', 'danger')
        return redirect(url_for('company.company_list'))

    company = Company(
        name=name,
        shipping_address=request.form.get('shipping_address'),
        manager=request.form.get('manager'),
        contact_person=request.form.get('contact_person'),
        online_contact=request.form.get('online_contact'),
        phone=request.form.get('phone'),
        remark=request.form.get('remark'),
    )
    db.session.add(company)
    db.session.commit()
    flash('公司添加成功', 'success')
    return redirect(url_for('company.company_list'))


@bp.route('/<int:company_id>/edit', methods=['POST'])
def edit_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.name = request.form.get('name', company.name)
    company.shipping_address = request.form.get('shipping_address', company.shipping_address)
    company.manager = request.form.get('manager', company.manager)
    company.contact_person = request.form.get('contact_person', company.contact_person)
    company.online_contact = request.form.get('online_contact', company.online_contact)
    company.phone = request.form.get('phone', company.phone)
    company.remark = request.form.get('remark', company.remark)
    db.session.commit()
    flash('公司信息已更新', 'success')
    return redirect(url_for('company.company_list'))
