from flask import Blueprint, render_template
from services.data_analysis import DataAnalysisService

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/reconciliation')
def reconciliation():
    data = DataAnalysisService.get_reconciliation()
    return render_template('analysis/reconciliation.html', data=data)


@analysis_bp.route('/arrears')
def arrears():
    data = DataAnalysisService.get_arrears()
    return render_template('analysis/arrears.html', data=data)
