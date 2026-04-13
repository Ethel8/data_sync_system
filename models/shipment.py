from db.database import db
from datetime import datetime


class Shipment(db.Model):
    """发货表"""
    __tablename__ = 'shipments'

    id = db.Column(db.Integer, primary_key=True)
    delivery_no = db.Column(db.String(64), comment='送货单号')
    customer_name = db.Column(db.String(128), comment='客户名称')
    terminal_name = db.Column(db.String(128), comment='终端名称')
    customer_order_no = db.Column(db.String(64), comment='客户订单号')
    customer_code = db.Column(db.String(64), comment='客户对应代码')
    material_name = db.Column(db.String(256), comment='物料名称')
    contract_qty = db.Column(db.Float, comment='合同数')
    delivery_qty = db.Column(db.Float, comment='本次送货数')
    document_date = db.Column(db.Date, comment='单据日期')
    logistics_no = db.Column(db.String(64), comment='物流单号')
    transport_method = db.Column(db.String(64), comment='运输方式')
    express_no = db.Column(db.String(64), comment='快递单号')
    box_count = db.Column(db.Integer, comment='箱数')
    box_no = db.Column(db.String(128), comment='箱号')

    import_batch = db.Column(db.String(64), comment='导入批次号')
    created_at = db.Column(db.DateTime, default=datetime.now)
