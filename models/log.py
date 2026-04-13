from db.database import db
from datetime import datetime


class OperationLog(db.Model):
    __tablename__ = 'operation_logs'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    action = db.Column(db.String(64), nullable=False, comment='操作类型: create/update_status/complete/anomaly/refund')
    old_value = db.Column(db.String(128), comment='变更前值')
    new_value = db.Column(db.String(128), comment='变更后值')
    remark = db.Column(db.String(256), comment='备注')

    created_at = db.Column(db.DateTime, default=datetime.now)
