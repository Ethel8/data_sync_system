from db.database import db
from datetime import datetime


class InvoiceCustomer(db.Model):
    """客户开票表"""
    __tablename__ = 'invoice_customer'

    id = db.Column(db.Integer, primary_key=True)
    delivery_location = db.Column(db.String(128), comment='指定地点')
    order_no = db.Column(db.String(64), comment='订单号')
    customer_product_code = db.Column(db.String(64), comment='客户产品代码')
    specification = db.Column(db.String(128), comment='规格')
    shipment_qty = db.Column(db.Float, comment='发货数')
    shipment_date = db.Column(db.Date, comment='发货日期')
    unit_price_incl_tax = db.Column(db.Float, comment='含税单价')
    amount_incl_tax = db.Column(db.Float, comment='含税金额')

    import_batch = db.Column(db.String(64), comment='导入批次号')
    created_at = db.Column(db.DateTime, default=datetime.now)
