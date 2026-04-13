from db.database import db


class MasterView(db.Model):
    """总表视图：关联5张表的所有信息，以销售订单号为主线"""
    __tablename__ = 'master_view'

    # 交期表字段
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
    unshipped_qty = db.Column(db.Float, comment='未出库数量(交期表)')
    review_delivery_date = db.Column(db.Date, comment='订单评审交期')
    order_status_sap = db.Column(db.String(32), comment='销售订单下达状态')
    planned_inbound_date = db.Column(db.Date, comment='计划应入库日期')
    customer_required_date = db.Column(db.Date, comment='客户要求交期')
    unstocked_qty = db.Column(db.Float, comment='未入库数量')
    stocked_qty = db.Column(db.Float, comment='已入库数量')
    shipped_qty = db.Column(db.Float, comment='已出库数量(交期表)')
    order_line_remark = db.Column(db.String(256), comment='销售订单行备注')
    customer_line = db.Column(db.String(64), comment='客户项次')

    # 发货表字段
    delivery_no = db.Column(db.String(64), comment='送货单号')
    terminal_name = db.Column(db.String(128), comment='终端名称')
    customer_code = db.Column(db.String(64), comment='客户对应代码')
    material_name = db.Column(db.String(256), comment='物料名称')
    contract_qty = db.Column(db.Float, comment='合同数')
    shipment_delivery_qty = db.Column(db.Float, comment='本次送货数')
    document_date = db.Column(db.Date, comment='单据日期')
    logistics_no = db.Column(db.String(64), comment='物流单号')
    transport_method = db.Column(db.String(64), comment='运输方式')
    express_no = db.Column(db.String(64), comment='快递单号')
    box_count = db.Column(db.Integer, comment='箱数')
    box_no = db.Column(db.String(128), comment='箱号')

    # 公司开票表字段
    customer_code_name = db.Column(db.String(256), comment='售达方客户代码名称')
    customer_po_no = db.Column(db.String(64), comment='客户采购订单号码')
    outbound_no = db.Column(db.String(64), comment='出库单号')
    invoice_qty = db.Column(db.Float, comment='开票数量')
    outbound_qty = db.Column(db.Float, comment='出库数量')
    uninvoiced_qty = db.Column(db.Float, comment='未开票数量')
    unit_price_excl_tax = db.Column(db.Float, comment='不含税单价')
    unit_price_incl_tax = db.Column(db.Float, comment='含税单价')
    uninvoiced_amount_excl_tax = db.Column(db.Float, comment='未开票不含税金额')
    uninvoiced_amount_incl_tax = db.Column(db.Float, comment='未开票价税合计')
    outbound_date = db.Column(db.Date, comment='出库日期')
    invoice_order_date = db.Column(db.Date, comment='订单日期(开票)')
    delivery_address = db.Column(db.String(256), comment='指定送货地址')

    # 客户开票表字段
    delivery_location = db.Column(db.String(128), comment='指定地点(客户开票)')
    customer_product_code = db.Column(db.String(64), comment='客户产品代码')
    specification = db.Column(db.String(128), comment='规格')
    inv_shipment_qty = db.Column(db.Float, comment='发货数(客户开票)')
    inv_shipment_date = db.Column(db.Date, comment='发货日期(客户开票)')
    inv_unit_price = db.Column(db.Float, comment='含税单价(客户开票)')
    inv_amount = db.Column(db.Float, comment='含税金额(客户开票)')

    # 公司明细表字段
    shipping_address = db.Column(db.String(256), comment='收货地址')
    company_manager = db.Column(db.String(64), comment='负责人')
    company_contact_person = db.Column(db.String(64), comment='联系人')
    company_online_contact = db.Column(db.String(128), comment='线上联系方式')
    company_phone = db.Column(db.String(32), comment='电话')

    # 订单状态
    status = db.Column(db.String(20), comment='订单状态')
    order_primary_status = db.Column(db.String(20), comment='订单一级状态')
    order_secondary_status = db.Column(db.String(256), comment='订单二级状态')

    __table_args__ = {'info': {'read_only': True}}
