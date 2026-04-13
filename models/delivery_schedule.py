from db.database import db
from datetime import datetime


class DeliverySchedule(db.Model):
    """交期表"""
    __tablename__ = 'delivery_schedule'

    id = db.Column(db.Integer, primary_key=True)
    mrp_controller = db.Column(db.String(64), comment='MRP控制者')
    sales_order_no = db.Column(db.String(64), comment='销售订单号')
    sales_order_line = db.Column(db.String(32), comment='销售订单行项目号')
    customer_name = db.Column(db.String(128), comment='客户名称')
    ship_to_name = db.Column(db.String(128), comment='送达方名称')
    create_date = db.Column(db.Date, comment='创建日期')
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

    import_batch = db.Column(db.String(64), comment='导入批次号')
    created_at = db.Column(db.DateTime, default=datetime.now)
