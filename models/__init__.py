from datetime import datetime
from app import db


class DeliverySchedule(db.Model):
    """交期表 - 由工厂日更上传"""
    __tablename__ = 'delivery_schedule'

    id = db.Column(db.Integer, primary_key=True)
    mrp_controller = db.Column(db.String(100), comment='MRP控制者')
    sales_order_no = db.Column(db.String(100), comment='销售订单号')
    sales_order_line_no = db.Column(db.String(100), comment='销售订单行项目号')
    customer_name = db.Column(db.String(200), comment='售达方客户名称')
    ship_to_name = db.Column(db.String(200), comment='送达方名称')
    create_date = db.Column(db.String(50), comment='创建日期')
    customer_contract_no = db.Column(db.String(200), comment='客户合同号')
    customer_material_code = db.Column(db.String(200), comment='客户物料代码')
    fara_external_code = db.Column(db.String(200), comment='法拉外码')
    order_quantity = db.Column(db.Float, comment='订单数量')
    unshipped_quantity = db.Column(db.Float, comment='未出库数量')
    order_review_date = db.Column(db.String(50), comment='订单评审交期')
    sales_order_status = db.Column(db.String(100), comment='销售订单下达状态')
    planned_warehouse_date = db.Column(db.String(50), comment='计划应入库日期')
    customer_required_date = db.Column(db.String(50), comment='客户要求交期')
    unwarehoused_quantity = db.Column(db.Float, comment='未入库数量')
    warehoused_quantity = db.Column(db.Float, comment='已入库数量')
    shipped_quantity = db.Column(db.Float, comment='已出库数量')
    sales_order_remark = db.Column(db.Text, comment='销售订单行备注')
    customer_item_no = db.Column(db.String(100), comment='客户项次')
    upload_time = db.Column(db.DateTime, default=datetime.now, comment='上传时间')


class Shipment(db.Model):
    """发货表 - 由工厂日更上传"""
    __tablename__ = 'shipment'

    id = db.Column(db.Integer, primary_key=True)
    delivery_note_no = db.Column(db.String(100), comment='送货单号')
    customer_name = db.Column(db.String(200), comment='售达方客户名称')
    ship_to_name = db.Column(db.String(200), comment='送达方名称')
    sales_order_no = db.Column(db.String(100), comment='销售订单号')
    customer_material_code = db.Column(db.String(200), comment='客户物料代码')
    fara_external_code = db.Column(db.String(200), comment='法拉外码')
    contract_quantity = db.Column(db.Float, comment='合同数')
    delivery_quantity = db.Column(db.Float, comment='本次送货数')
    ship_date = db.Column(db.String(50), comment='发货日期')
    logistics_no = db.Column(db.String(200), comment='物流单号')
    transport_method = db.Column(db.String(100), comment='运输方式')
    express_no = db.Column(db.String(200), comment='快递单号')
    box_count = db.Column(db.Float, comment='箱数')
    box_no = db.Column(db.String(200), comment='箱号')
    upload_time = db.Column(db.DateTime, default=datetime.now, comment='上传时间')


class FactoryInvoice(db.Model):
    """公司开票表 - 由工厂月更上传"""
    __tablename__ = 'factory_invoice'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), comment='售达方客户名称')
    sales_order_no = db.Column(db.String(100), comment='销售订单号')
    customer_material_code = db.Column(db.String(200), comment='客户物料代码')
    customer_purchase_order_no = db.Column(db.String(200), comment='客户采购订单号码')
    fara_external_code = db.Column(db.String(200), comment='法拉外码')
    warehouse_no = db.Column(db.String(200), comment='出库单号')
    invoice_quantity = db.Column(db.Float, comment='开票数量')
    warehouse_quantity = db.Column(db.Float, comment='出库数量')
    uninvoiced_quantity = db.Column(db.Float, comment='未开票数量')
    price_excl_tax = db.Column(db.Float, comment='不含税单价')
    price_incl_tax = db.Column(db.Float, comment='含税单价')
    uninvoiced_amount_excl_tax = db.Column(db.Float, comment='未开票不含税金额')
    uninvoiced_amount_incl_tax = db.Column(db.Float, comment='未开票价税合计')
    ship_date = db.Column(db.String(50), comment='发货日期')
    order_date = db.Column(db.String(50), comment='订单日期')
    delivery_address = db.Column(db.String(500), comment='指定送货地址')
    upload_time = db.Column(db.DateTime, default=datetime.now, comment='上传时间')


class CustomerInvoice(db.Model):
    """客户开票表 - 给客户月更"""
    __tablename__ = 'customer_invoice'

    id = db.Column(db.Integer, primary_key=True)
    ship_to_name = db.Column(db.String(200), comment='送达方名称')
    sales_order_no = db.Column(db.String(100), comment='销售订单号')
    customer_material_code = db.Column(db.String(200), comment='客户物料代码')
    fara_external_code = db.Column(db.String(200), comment='法拉外码')
    shipped_quantity = db.Column(db.Float, comment='发货数')
    ship_date = db.Column(db.String(50), comment='发货日期')
    price_incl_tax = db.Column(db.Float, comment='含税单价')
    amount_incl_tax = db.Column(db.Float, comment='含税金额')
    upload_time = db.Column(db.DateTime, default=datetime.now, comment='上传时间')


class Company(db.Model):
    """客户明细表 - 不定期更新"""
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    ship_to_name = db.Column(db.String(200), comment='送达方名称')
    delivery_address = db.Column(db.String(500), comment='指定送货地址')
    manager = db.Column(db.String(100), comment='负责人')
    contact_person = db.Column(db.String(100), comment='联系人')
    online_contact = db.Column(db.String(200), comment='线上联系方式')
    phone = db.Column(db.String(100), comment='电话')
    upload_time = db.Column(db.DateTime, default=datetime.now, comment='更新时间')


class Order(db.Model):
    """订单主表 - 由输入表联动计算得出，不可导入"""
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    sales_order_no = db.Column(db.String(100), comment='销售订单号')
    ship_to_name = db.Column(db.String(200), comment='送达方名称')
    create_date = db.Column(db.String(50), comment='创建日期')
    fara_external_code = db.Column(db.String(200), comment='法拉外码')
    order_quantity = db.Column(db.Float, comment='订单数量')
    ship_date = db.Column(db.String(50), comment='发货日期')
    shipped_quantity = db.Column(db.Float, default=0, comment='已发货数量')
    factory_invoice_quantity = db.Column(db.Float, default=0, comment='公司开票数量')
    customer_invoice_quantity = db.Column(db.Float, default=0, comment='客户开票数量')
    purchase_price_excl_tax = db.Column(db.Float, default=0, comment='买入单价不含税')
    customer_payable_incl_tax = db.Column(db.Float, default=0, comment='客户应付含税金额')
    manager = db.Column(db.String(100), comment='负责人')
    order_status = db.Column(db.String(20), default='正常', comment='订单状态：正常/异常/完结/退单')
    order_progress = db.Column(db.String(50), default='生产中', comment='订单进度')
    factory_invoice_status = db.Column(db.String(50), default='未开票', comment='公司开票状态')
    customer_invoice_status = db.Column(db.String(50), default='未开票', comment='客户开票状态')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    logs = db.relationship('OrderLog', backref='order', lazy=True)


class OrderLog(db.Model):
    """订单操作日志"""
    __tablename__ = 'order_log'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), comment='关联订单')
    action = db.Column(db.String(100), comment='操作类型')
    detail = db.Column(db.Text, comment='操作详情')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='操作时间')


class SystemLog(db.Model):
    """系统操作日志"""
    __tablename__ = 'system_log'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), comment='操作类型')
    operator = db.Column(db.String(100), comment='操作人')
    detail = db.Column(db.Text, comment='操作详情')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='操作时间')
