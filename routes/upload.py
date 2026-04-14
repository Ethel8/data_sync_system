import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.excel_import import ExcelImportService

upload_bp = Blueprint('upload', __name__)

TABLE_LABELS = {
    'delivery_schedule': '交期表',
    'shipment': '发货表',
    'factory_invoice': '公司开票表',
    'customer_invoice': '客户开票表',
    'company': '公司明细表',
}


@upload_bp.route('/')
def index():
    return render_template('upload.html', table_labels=TABLE_LABELS)


@upload_bp.route('/', methods=['POST'])
def upload_file():
    table_type = request.form.get('table_type')
    file = request.files.get('file')

    if not file or not file.filename:
        flash('请选择文件', 'danger')
        return redirect(url_for('upload.index'))

    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('仅支持 .xlsx 或 .xls 格式', 'danger')
        return redirect(url_for('upload.index'))

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)

    success_count, errors = ExcelImportService.parse_excel(file_path, table_type)

    label = TABLE_LABELS.get(table_type, table_type)
    if errors and success_count == 0:
        flash(f'{label}导入失败: {"; ".join(errors[:3])}', 'danger')
    elif errors:
        flash(f'{label}导入 {success_count} 条，但有 {len(errors)} 条错误: {"; ".join(errors[:3])}', 'warning')
    else:
        flash(f'{label}导入成功，共 {success_count} 条记录', 'success')

    return redirect(url_for('upload.index'))
