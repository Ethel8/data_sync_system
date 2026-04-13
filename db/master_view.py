"""
创建总表视图 master_view 的SQL
关联方式：以交期表为主表，LEFT JOIN 其余4张表
- 发货表：通过 客户订单号 = 交期表.销售订单号
- 公司开票表：通过 销售订单号 = 交期表.销售订单号
- 客户开票表：通过 订单号 = 交期表.销售订单号
- 公司明细表：通过 公司名称 = 交期表.客户名称
- 订单状态：通过 orders 表关联
"""

CREATE_MASTER_VIEW_SQL = """
CREATE VIEW IF NOT EXISTS master_view AS
SELECT
    ds.id,
    -- 交期表
    ds.mrp_controller,
    ds.sales_order_no,
    ds.sales_order_line,
    ds.customer_name,
    ds.ship_to_name,
    ds.create_date,
    ds.customer_contract_no,
    ds.customer_material_code,
    ds.falah_code,
    ds.order_quantity,
    ds.unshipped_qty,
    ds.review_delivery_date,
    ds.order_status_sap,
    ds.planned_inbound_date,
    ds.customer_required_date,
    ds.unstocked_qty,
    ds.stocked_qty,
    ds.shipped_qty,
    ds.order_line_remark,
    ds.customer_line,
    -- 发货表
    s.delivery_no,
    s.terminal_name,
    s.customer_code,
    s.material_name,
    s.contract_qty,
    s.delivery_qty AS shipment_delivery_qty,
    s.document_date,
    s.logistics_no,
    s.transport_method,
    s.express_no,
    s.box_count,
    s.box_no,
    -- 公司开票表
    inf.customer_code_name,
    inf.customer_po_no,
    inf.outbound_no,
    inf.invoice_qty,
    inf.outbound_qty,
    inf.uninvoiced_qty,
    inf.unit_price_excl_tax,
    inf.unit_price_incl_tax,
    inf.uninvoiced_amount_excl_tax,
    inf.uninvoiced_amount_incl_tax,
    inf.outbound_date,
    inf.order_date AS invoice_order_date,
    inf.delivery_address,
    -- 客户开票表
    inc.delivery_location,
    inc.customer_product_code,
    inc.specification,
    inc.shipment_qty AS inv_shipment_qty,
    inc.shipment_date AS inv_shipment_date,
    inc.unit_price_incl_tax AS inv_unit_price,
    inc.amount_incl_tax AS inv_amount,
    -- 公司明细表
    c.shipping_address,
    c.manager AS company_manager,
    c.contact_person AS company_contact_person,
    c.online_contact AS company_online_contact,
    c.phone AS company_phone,
    -- 订单状态
    o.status,
    o.status AS order_primary_status,
    o.status_remark AS order_secondary_status
FROM delivery_schedule ds
LEFT JOIN shipments s ON s.customer_order_no = ds.sales_order_no
LEFT JOIN invoice_factory inf ON inf.sales_order_no = ds.sales_order_no
LEFT JOIN invoice_customer inc ON inc.order_no = ds.sales_order_no
LEFT JOIN companies c ON c.name = ds.customer_name
LEFT JOIN orders o ON o.order_no = ds.sales_order_no
"""


def create_master_view(engine):
    """在数据库中创建总表视图"""
    with engine.connect() as conn:
        conn.execute(text(CREATE_MASTER_VIEW_SQL))
        conn.commit()
