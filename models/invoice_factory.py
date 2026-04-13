from db.database import db
from datetime import datetime


class InvoiceFactory(db.Model):
    """公司开票表（工厂侧）"""
    __tablename__ = 'invoice_factory'

    id = db.Column(db.Integer, primary_key=True)
    customer_code_name = db.Column(db.String(256), comment='售达方客户代码名称')
    sales_order_no = db.Column(db.String(64), comment='销售订单号')
    customer_material_code = db.Column(db.String(64), comment='客户物料代码')
    customer_po_no = db.Column(db.String(64), comment='客户采购订单号码')
    falah_code = db.Column(db.String(64), comment='法拉外码')
    outbound_no = db.Column(db.String(64), comment='出库单号')
    invoice_qty = db.Column(db.Float, comment='开票数量')
    outbound_qty = db.Column(db.Float, comment='出库数量')
    uninvoiced_qty = db.Column(db.Float, comment='未开票数量')
    unit_price_excl_tax = db.Column(db.Float, comment='不含税单价')
    unit_price_incl_tax = db.Column(db.Float, comment='含税单价')
    uninvoiced_amount_excl_tax = db.Column(db.Float, comment='未开票不含税金额')
    uninvoiced_amount_incl_tax = db.Column(db.Float, comment='未开票价税合计')
    outbound_date = db.Column(db.Date, comment='出库日期')
    order_date = db.Column(db.Date, comment='订单日期')
    delivery_address = db.Column(db.String(256), comment='指定送货地址')

    import_batch = db.Column(db.String(64), comment='导入批次号')
    created_at = db.Column(db.DateTime, default=datetime.now)
