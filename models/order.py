from db.database import db
from datetime import datetime


class OrderStatus:
    """订单一级状态"""
    NORMAL = 'normal'
    ANOMALY = 'anomaly'
    COMPLETED = 'completed'
    REFUNDED = 'refunded'

    LABELS = {
        'normal': '正常',
        'anomaly': '异常',
        'completed': '完结',
        'refunded': '退单',
    }


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(64), unique=True, nullable=False, comment='销售订单号')
    order_line = db.Column(db.String(32), comment='销售订单行项目号')
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), comment='关联公司')
    customer_contract_no = db.Column(db.String(64), comment='客户合同号')
    customer_material_code = db.Column(db.String(64), comment='客户物料代码')
    falah_code = db.Column(db.String(64), comment='法拉外码')
    order_quantity = db.Column(db.Float, comment='订单数量')
    unshipped_qty = db.Column(db.Float, comment='未出库数量')
    review_delivery_date = db.Column(db.Date, comment='订单评审交期')
    order_status_sap = db.Column(db.String(32), comment='销售订单下达状态')
    planned_inbound_date = db.Column(db.Date, comment='计划应入库日期')
    customer_required_date = db.Column(db.Date, comment='客户要求交期')
    unstocked_qty = db.Column(db.Float, comment='未入库数量')
    stocked_qty = db.Column(db.Float, comment='已入库数量')
    shipped_qty = db.Column(db.Float, comment='已出库数量')
    order_line_remark = db.Column(db.String(256), comment='销售订单行备注')
    customer_line = db.Column(db.String(64), comment='客户项次')

    # 状态
    status = db.Column(db.String(20), default=OrderStatus.NORMAL, comment='一级状态')
    status_remark = db.Column(db.String(256), comment='状态备注')

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at = db.Column(db.DateTime, comment='完结时间')

    # 关联
    company = db.relationship('Company', backref='orders')
    logs = db.relationship('OperationLog', backref='order', lazy='dynamic')

    def get_status_label(self):
        return OrderStatus.LABELS.get(self.status, self.status)
