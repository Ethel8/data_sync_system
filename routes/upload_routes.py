import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from services.excel_import import handle_import
from config import ALLOWED_TABLES, UPLOAD_FOLDER

bp = Blueprint('upload', __name__, url_prefix='/upload')


@bp.route('/', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        table_type = request.form.get('table_type')
        file = request.files.get('file')

        if not table_type or table_type not in ALLOWED_TABLES:
            flash('请选择有效的表类型', 'danger')
            return redirect(url_for('upload.upload_page'))

        if not file or not file.filename.endswith(('.xlsx', '.xls')):
            flash('请上传 .xlsx 或 .xls 文件', 'danger')
            return redirect(url_for('upload.upload_page'))

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            result = handle_import(table_type, filepath)
            flash(f'导入成功: {result}', 'success')
        except Exception as e:
            flash(f'导入失败: {str(e)}', 'danger')

        return redirect(url_for('upload.upload_page'))

    return render_template('upload.html', table_types=ALLOWED_TABLES)
