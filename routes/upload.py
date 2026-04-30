from flask import Blueprint, render_template, request, jsonify
from services.excel_import import import_excel

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/', methods=['GET'])
def index():
    """上传页面"""
    return render_template('upload.html')


@upload_bp.route('/<table_type>', methods=['POST'])
def upload_file(table_type):
    """处理 Excel 上传"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '请选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '文件名为空'}), 400

    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'error': '仅支持 Excel 文件（.xlsx/.xls）'}), 400

    success, errors, filepath = import_excel(file, table_type)

    return jsonify({
        'success': True,
        'data': {
            'success_count': success,
            'errors': errors,
            'saved_path': filepath,
        }
    })
