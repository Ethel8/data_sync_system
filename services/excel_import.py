"""Excel 表导入服务，支持5种数据表"""
import uuid
import openpyxl
from db.database import db
from models.company import Company
from models.order import Order, OrderStatus
from models.delivery_schedule import DeliverySchedule
from models.shipment import Shipment
from models.invoice_factory import InvoiceFactory
from models.invoice_customer import InvoiceCustomer


def parse_excel(file_path):
    """解析Excel文件，返回表头和数据行"""
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if not rows:
        raise ValueError('Excel文件为空')
    headers = [str(h).strip() if h else f'col_{i}' for i, h in enumerate(rows[0])]
    data = [dict(zip(headers, row)) for row in rows[1:] if any(cell is not None for cell in row)]
    return headers, data


def _new_batch():
    return str(uuid.uuid4())[:8]


# ==================== 交期表 ====================

_DELIVERY_FIELD_MAP = {
    'MRP控制者': 'mrp_controller',
    '销售订单号': 'sales_order_no',
    '销售订单行项目号': 'sales_order_line',
    '客户名称': 'customer_name',
    '送达方名称': 'ship_to_name',
    '创建日期': 'create_date',
    '客户合同号': 'customer_contract_no',
    '客户物料代码': 'customer_material_code',
    '法拉外码': 'falah_code',
    '订单数量': 'order_quantity',
    '未出库数量': 'unshipped_qty',
    '订单评审交期': 'review_delivery_date',
    '销售订单下达状态': 'order_status_sap',
    '计划应入库日期': 'planned_inbound_date',
    '客户要求交期': 'customer_required_date',
    '未入库数量': 'unstocked_qty',
    '已入库数量': 'stocked_qty',
    '已出库数量': 'shipped_qty',
    '销售订单行备注': 'order_line_remark',
    '客户项次': 'customer_line',
}


def import_delivery_schedule(file_path):
    """导入交期表 → 创建订单 + 存原始数据"""
    headers, data = parse_excel(file_path)
    batch = _new_batch()
    created = 0

    for row in data:
        # 存原始数据
        ds = DeliverySchedule(import_batch=batch)
        for cn, field in _DELIVERY_FIELD_MAP.items():
            val = row.get(cn)
            if val is not None:
                setattr(ds, field, val)
        db.session.add(ds)

        # 创建/更新订单（按销售订单号去重）
        order_no = row.get('销售订单号')
        if order_no:
            existing = Order.query.filter_by(order_no=order_no).first()
            if not existing:
                # 关联公司
                company_name = row.get('客户名称')
                company = None
                if company_name:
                    company = Company.query.filter_by(name=company_name).first()
                    if not company:
                        company = Company(name=company_name)
                        db.session.add(company)
                        db.session.flush()

                order = Order(
                    order_no=order_no,
                    company_id=company.id if company else None,
                    order_line=row.get('销售订单行项目号'),
                    customer_contract_no=row.get('客户合同号'),
                    customer_material_code=row.get('客户物料代码'),
                    falah_code=row.get('法拉外码'),
                    order_quantity=row.get('订单数量'),
                    unshipped_qty=row.get('未出库数量'),
                    review_delivery_date=row.get('订单评审交期'),
                    order_status_sap=row.get('销售订单下达状态'),
                    planned_inbound_date=row.get('计划应入库日期'),
                    customer_required_date=row.get('客户要求交期'),
                    unstocked_qty=row.get('未入库数量'),
                    stocked_qty=row.get('已入库数量'),
                    shipped_qty=row.get('已出库数量'),
                    order_line_remark=row.get('销售订单行备注'),
                    customer_line=row.get('客户项次'),
                    status=OrderStatus.NORMAL,
                )
                db.session.add(order)
                created += 1

    db.session.commit()
    return {'success': True, 'created': created, 'total': len(data), 'batch': batch}


# ==================== 发货表 ====================

_SHIPMENT_FIELD_MAP = {
    '送货单号': 'delivery_no',
    '客户名称': 'customer_name',
    '终端名称': 'terminal_name',
    '客户订单号': 'customer_order_no',
    '客户对应代码': 'customer_code',
    '物料名称': 'material_name',
    '合同数': 'contract_qty',
    '本次送货数': 'delivery_qty',
    '单据日期': 'document_date',
    '物流单号': 'logistics_no',
    '运输方式': 'transport_method',
    '快递单号': 'express_no',
    '箱数': 'box_count',
    '箱号': 'box_no',
}


def import_shipment(file_path):
    """导入发货表 → 存原始数据 + 更新订单出库数量"""
    headers, data = parse_excel(file_path)
    batch = _new_batch()
    updated = 0

    for row in data:
        st = Shipment(import_batch=batch)
        for cn, field in _SHIPMENT_FIELD_MAP.items():
            val = row.get(cn)
            if val is not None:
                setattr(st, field, val)
        db.session.add(st)

        # 按客户订单号匹配更新订单
        customer_order_no = row.get('客户订单号')
        if customer_order_no:
            order = Order.query.filter_by(order_no=customer_order_no).first()
            if order:
                delivery_qty = row.get('本次送货数')
                if delivery_qty is not None:
                    order.shipped_qty = (order.shipped_qty or 0) + delivery_qty
                    order.unshipped_qty = max((order.order_quantity or 0) - order.shipped_qty, 0)
                    updated += 1

    db.session.commit()
    return {'success': True, 'updated': updated, 'total': len(data), 'batch': batch}


# ==================== 公司开票表 ====================

_INVOICE_FACTORY_FIELD_MAP = {
    '售达方客户代码名称': 'customer_code_name',
    '销售订单号': 'sales_order_no',
    '客户物料代码': 'customer_material_code',
    '客户采购订单号码': 'customer_po_no',
    '法拉外码': 'falah_code',
    '出库单号': 'outbound_no',
    '开票数量': 'invoice_qty',
    '出库数量': 'outbound_qty',
    '未开票数量': 'uninvoiced_qty',
    '不含税单价': 'unit_price_excl_tax',
    '含税单价': 'unit_price_incl_tax',
    '未开票不含税金额': 'uninvoiced_amount_excl_tax',
    '未开票价税合计': 'uninvoiced_amount_incl_tax',
    '出库日期': 'outbound_date',
    '订单日期': 'order_date',
    '指定送货地址': 'delivery_address',
}


def import_invoice_factory(file_path):
    """导入公司开票表（工厂侧）"""
    headers, data = parse_excel(file_path)
    batch = _new_batch()
    created = 0

    for row in data:
        inv = InvoiceFactory(import_batch=batch)
        for cn, field in _INVOICE_FACTORY_FIELD_MAP.items():
            val = row.get(cn)
            if val is not None:
                setattr(inv, field, val)
        db.session.add(inv)
        created += 1

    db.session.commit()
    return {'success': True, 'created': created, 'total': len(data), 'batch': batch}


# ==================== 客户开票表 ====================

_INVOICE_CUSTOMER_FIELD_MAP = {
    '指定地点': 'delivery_location',
    '订单号': 'order_no',
    '客户产品代码': 'customer_product_code',
    '规格': 'specification',
    '发货数': 'shipment_qty',
    '发货日期': 'shipment_date',
    '含税单价': 'unit_price_incl_tax',
    '含税金额': 'amount_incl_tax',
}


def import_invoice_customer(file_path):
    """导入客户开票表"""
    headers, data = parse_excel(file_path)
    batch = _new_batch()
    created = 0

    for row in data:
        inv = InvoiceCustomer(import_batch=batch)
        for cn, field in _INVOICE_CUSTOMER_FIELD_MAP.items():
            val = row.get(cn)
            if val is not None:
                setattr(inv, field, val)
        db.session.add(inv)
        created += 1

    db.session.commit()
    return {'success': True, 'created': created, 'total': len(data), 'batch': batch}


# ==================== 公司明细表 ====================

_COMPANY_FIELD_MAP = {
    '公司名称': 'name',
    '收货地址': 'shipping_address',
    '负责人': 'manager',
    '联系人': 'contact_person',
    '线上联系方式': 'online_contact',
    '电话': 'phone',
}


def import_company(file_path):
    """导入公司明细表"""
    headers, data = parse_excel(file_path)
    created = 0
    updated = 0

    for row in data:
        company_name = row.get('公司名称')
        if not company_name:
            continue

        company = Company.query.filter_by(name=company_name).first()
        is_new = company is None
        if is_new:
            company = Company(name=company_name)

        for cn, field in _COMPANY_FIELD_MAP.items():
            val = row.get(cn)
            if val is not None and field != 'name':
                setattr(company, field, val)

        db.session.add(company)
        if is_new:
            created += 1
        else:
            updated += 1

    db.session.commit()
    return {'success': True, 'created': created, 'updated': updated, 'total': len(data)}


# ==================== 调度 ====================

IMPORT_HANDLERS = {
    'delivery_schedule': import_delivery_schedule,
    'shipment': import_shipment,
    'invoice_factory': import_invoice_factory,
    'invoice_customer': import_invoice_customer,
    'company': import_company,
}


def handle_import(table_type, file_path):
    """根据表类型调用对应的导入函数"""
    handler = IMPORT_HANDLERS.get(table_type)
    if not handler:
        raise ValueError(f'不支持的表类型: {table_type}')
    return handler(file_path)
