from flask import Blueprint, render_template
from services.analysis_service import get_reconciliation, get_arrears

bp = Blueprint('analysis', __name__, url_prefix='/analysis')


@bp.route('/reconciliation')
def reconciliation():
    data = get_reconciliation()
    return render_template('analysis/reconciliation.html', **data)


@bp.route('/arrears')
def arrears():
    data = get_arrears()
    return render_template('analysis/arrears.html', **data)
