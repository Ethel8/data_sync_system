import os
import shutil
from datetime import datetime
import openpyxl
from app import db
from models import (DeliverySchedule, Shipment, FactoryInvoice,
                    CustomerInvoice, Company, Order, OrderLog, SystemLog)
from services.order_status_engine import recalculate_order_status, update_all_orders_manager


def _safe_float(val):
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _safe_str(val):
    if val is None:
        return ''
    return str(val).strip()


def _save_upload_file(file, table_type):
    """保存上传的 Excel 文件，文件名前缀加8位日期"""
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', table_type)
    os.makedirs(upload_folder, exist_ok=True)
    date_prefix = datetime.now().strftime('%Y%m%d')
    filename = f"{date_prefix}_{file.filename}"
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filepath


# ========== 表头映射 ==========

DELIVERY_SCHEDULE_MAP = {
    'MRP控制者': 'mrp_controller',
    '销售订单号': 'sales_order_no',
    '销售订单行项目号': 'sales_order_line_no',
    '售达方客户名称': 'customer_name',
    '送达方名称': 'ship_to_name',
    '创建日期': 'create_date',
    '客户合同号': 'customer_contract_no',
    '客户物料代码': 'customer_material_code',
    '法拉外码': 'fara_external_code',
    '订单数量': 'order_quantity',
    '未出库数量': 'unshipped_quantity',
    '订单评审交期': 'order_review_date',
    '销售订单下达状态': 'sales_order_status',
    '计划应入库日期': 'planned_warehouse_date',
    '客户要求交期': 'customer_required_date',
    '未入库数量': 'unwarehoused_quantity',
    '已入库数量': 'warehoused_quantity',
    '已出库数量': 'shipped_quantity',
    '销售订单行备注': 'sales_order_remark',
    '客户项次': 'customer_item_no',
}

SHIPMENT_MAP = {
    '送货单号': 'delivery_note_no',
    '售达方客户名称': 'customer_name',
    '送达方名称': 'ship_to_name',
    '销售订单号': 'sales_order_no',
    '客户物料代码': 'customer_material_code',
    '法拉外码': 'fara_external_code',
    '合同数': 'contract_quantity',
    '本次送货数': 'delivery_quantity',
    '发货日期': 'ship_date',
    '物流单号': 'logistics_no',
    '运输方式': 'transport_method',
    '快递单号': 'express_no',
    '箱数': 'box_count',
    '箱号': 'box_no',
}

FACTORY_INVOICE_MAP = {
    '售达方客户名称': 'customer_name',
    '销售订单号': 'sales_order_no',
    '客户物料代码': 'customer_material_code',
    '客户采购订单号码': 'customer_purchase_order_no',
    '法拉外码': 'fara_external_code',
    '出库单号': 'warehouse_no',
    '开票数量': 'invoice_quantity',
    '出库数量': 'warehouse_quantity',
    '未开票数量': 'uninvoiced_quantity',
    '不含税单价': 'price_excl_tax',
    '含税单价': 'price_incl_tax',
    '未开票不含税金额': 'uninvoiced_amount_excl_tax',
    '未开票价税合计': 'uninvoiced_amount_incl_tax',
    '发货日期': 'ship_date',
    '订单日期': 'order_date',
    '指定送货地址': 'delivery_address',
}

CUSTOMER_INVOICE_MAP = {
    '送达方名称': 'ship_to_name',
    '销售订单号': 'sales_order_no',
    '客户物料代码': 'customer_material_code',
    '法拉外码': 'fara_external_code',
    '发货数': 'shipped_quantity',
    '发货日期': 'ship_date',
    '含税单价': 'price_incl_tax',
    '含税金额': 'amount_incl_tax',
}

COMPANY_MAP = {
    '送达方名称': 'ship_to_name',
    '指定送货地址': 'delivery_address',
    '负责人': 'manager',
    '联系人': 'contact_person',
    '线上联系方式': 'online_contact',
    '电话': 'phone',
}

TABLE_CONFIGS = {
    'delivery_schedule': {
        'map': DELIVERY_SCHEDULE_MAP,
        'model': DeliverySchedule,
    },
    'shipment': {
        'map': SHIPMENT_MAP,
        'model': Shipment,
    },
    'factory_invoice': {
        'map': FACTORY_INVOICE_MAP,
        'model': FactoryInvoice,
    },
    'customer_invoice': {
        'map': CUSTOMER_INVOICE_MAP,
        'model': CustomerInvoice,
    },
    'company': {
        'map': COMPANY_MAP,
        'model': Company,
    },
}

FLOAT_FIELDS = {
    'delivery_schedule': {'order_quantity', 'unshipped_quantity', 'unwarehoused_quantity', 'warehoused_quantity', 'shipped_quantity'},
    'shipment': {'contract_quantity', 'delivery_quantity', 'box_count'},
    'factory_invoice': {'invoice_quantity', 'warehouse_quantity', 'uninvoiced_quantity', 'price_excl_tax', 'price_incl_tax', 'uninvoiced_amount_excl_tax', 'uninvoiced_amount_incl_tax'},
    'customer_invoice': {'shipped_quantity', 'price_incl_tax', 'amount_incl_tax'},
    'company': set(),
}


def _parse_rows(file_path, field_map, float_fields):
    """解析 Excel，返回 (col_mapping, rows)"""
    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not rows:
        return None, []

    header = [_safe_str(cell) for cell in rows[0]]
    col_mapping = {}
    for idx, col_name in enumerate(header):
        if col_name in field_map:
            col_mapping[idx] = field_map[col_name]

    if not col_mapping:
        return None, []

    parsed_rows = []
    for row in rows[1:]:
        data = {}
        for col_idx, field_name in col_mapping.items():
            value = row[col_idx] if col_idx < len(row) else None
            if field_name in float_fields:
                data[field_name] = _safe_float(value)
            else:
                data[field_name] = _safe_str(value)
        parsed_rows.append(data)

    return col_mapping, parsed_rows


def import_delivery_schedule(file_path):
    """1.2 交期表导入"""
    col_mapping, rows = _parse_rows(file_path, DELIVERY_SCHEDULE_MAP, FLOAT_FIELDS['delivery_schedule'])
    if col_mapping is None:
        return 0, ['未匹配到有效列名']

    success_count = 0
    errors = []
    for row in rows:
        try:
            # 索引：销售订单号 + 法拉外码 + 订单数量
            existing = DeliverySchedule.query.filter_by(
                sales_order_no=row['sales_order_no'],
                fara_external_code=row['fara_external_code'],
                order_quantity=row['order_quantity']
            ).first()

            if existing:
                # 覆盖更新
                for key, value in row.items():
                    setattr(existing, key, value)
                # 同步更新订单主表的 order_quantity
                order = Order.query.filter_by(
                    sales_order_no=row['sales_order_no'],
                    fara_external_code=row['fara_external_code']
                ).first()
                if order:
                    order.order_quantity = row['order_quantity']
                    recalculate_order_status(order)
            else:
                # 创建新条目
                ds = DeliverySchedule(**row)
                db.session.add(ds)
                # 同步在订单主表创建
                order = Order.query.filter_by(
                    sales_order_no=row['sales_order_no'],
                    fara_external_code=row['fara_external_code']
                ).first()
                if not order:
                    order = Order(
                        sales_order_no=row['sales_order_no'],
                        ship_to_name=row.get('ship_to_name', ''),
                        create_date=row.get('create_date', ''),
                        fara_external_code=row['fara_external_code'],
                        order_quantity=row['order_quantity'],
                    )
                    db.session.add(order)
                    db.session.add(OrderLog(order_id=order.id, action='创建订单', detail='从交期表自动创建'))
                else:
                    order.order_quantity = row['order_quantity']
                recalculate_order_status(order)

            success_count += 1
        except Exception as e:
            errors.append(f'行解析失败: {str(e)}')

    db.session.commit()
    return success_count, errors


def import_shipment(file_path):
    """1.3 发货表导入"""
    col_mapping, rows = _parse_rows(file_path, SHIPMENT_MAP, FLOAT_FIELDS['shipment'])
    if col_mapping is None:
        return 0, ['未匹配到有效列名']

    success_count = 0
    errors = []
    for row in rows:
        try:
            # 每次创建新条目
            s = Shipment(**row)
            db.session.add(s)

            # 在发货表数据库中索引：送达方名称+销售订单号+法拉外码+合同数
            matched_shipments = Shipment.query.filter_by(
                ship_to_name=row['ship_to_name'],
                sales_order_no=row['sales_order_no'],
                fara_external_code=row['fara_external_code'],
                contract_quantity=row['contract_quantity']
            ).all()

            if matched_shipments:
                # 所匹配条目的"本次送货数"求和
                total_delivered = sum(_safe_float(m.delivery_quantity) for m in matched_shipments)
            else:
                total_delivered = _safe_float(row['delivery_quantity'])

            # 更新订单主表
            order = Order.query.filter_by(
                sales_order_no=row['sales_order_no'],
                fara_external_code=row['fara_external_code']
            ).first()
            if order:
                order.shipped_quantity = total_delivered
                # 更新发货日期
                if row.get('ship_date'):
                    order.ship_date = row['ship_date']
                recalculate_order_status(order)

            success_count += 1
        except Exception as e:
            errors.append(f'行解析失败: {str(e)}')

    db.session.commit()
    return success_count, errors


def import_factory_invoice(file_path):
    """1.4 公司开票表导入"""
    col_mapping, rows = _parse_rows(file_path, FACTORY_INVOICE_MAP, FLOAT_FIELDS['factory_invoice'])
    if col_mapping is None:
        return 0, ['未匹配到有效列名']

    success_count = 0
    errors = []
    for row in rows:
        try:
            # 索引：销售订单号 + 法拉外码
            existing = FactoryInvoice.query.filter_by(
                sales_order_no=row['sales_order_no'],
                fara_external_code=row['fara_external_code']
            ).first()

            if existing:
                for key, value in row.items():
                    setattr(existing, key, value)
            else:
                fi = FactoryInvoice(**row)
                db.session.add(fi)

            # 更新订单主表
            matched_orders = Order.query.filter_by(
                sales_order_no=row['sales_order_no'],
                fara_external_code=row['fara_external_code']
            ).all()

            if len(matched_orders) > 1:
                errors.append(f'订单不唯一: {row["sales_order_no"]}/{row["fara_external_code"]}，匹配到{len(matched_orders)}条，跳过')
                continue

            if matched_orders:
                order = matched_orders[0]
                order.factory_invoice_quantity = _safe_float(row['invoice_quantity'])
                order.purchase_price_excl_tax = _safe_float(row['price_excl_tax'])
                recalculate_order_status(order)

            success_count += 1
        except Exception as e:
            errors.append(f'行解析失败: {str(e)}')

    db.session.commit()
    return success_count, errors


def import_customer_invoice(file_path):
    """1.5 客户开票表导入"""
    col_mapping, rows = _parse_rows(file_path, CUSTOMER_INVOICE_MAP, FLOAT_FIELDS['customer_invoice'])
    if col_mapping is None:
        return 0, ['未匹配到有效列名']

    success_count = 0
    errors = []
    for row in rows:
        try:
            # 每次创建新条目
            ci = CustomerInvoice(**row)
            db.session.add(ci)

            # 在客户开票表索引：送达方名称+销售订单号+法拉外码
            matched = CustomerInvoice.query.filter_by(
                ship_to_name=row['ship_to_name'],
                sales_order_no=row['sales_order_no'],
                fara_external_code=row['fara_external_code']
            ).all()

            if matched:
                total_shipped = sum(_safe_float(m.shipped_quantity) for m in matched)
                total_amount = sum(_safe_float(m.amount_incl_tax) for m in matched)
            else:
                total_shipped = _safe_float(row['shipped_quantity'])
                total_amount = _safe_float(row['amount_incl_tax'])

            # 更新订单主表
            order = Order.query.filter_by(
                sales_order_no=row['sales_order_no'],
                fara_external_code=row['fara_external_code']
            ).first()
            if order:
                order.customer_invoice_quantity = total_shipped
                order.customer_payable_incl_tax = total_amount
                recalculate_order_status(order)

            success_count += 1
        except Exception as e:
            errors.append(f'行解析失败: {str(e)}')

    db.session.commit()
    return success_count, errors


def import_company(file_path):
    """1.6 客户明细表导入"""
    col_mapping, rows = _parse_rows(file_path, COMPANY_MAP, FLOAT_FIELDS['company'])
    if col_mapping is None:
        return 0, ['未匹配到有效列名']

    success_count = 0
    errors = []
    for row in rows:
        try:
            existing = Company.query.filter_by(
                ship_to_name=row['ship_to_name']
            ).first()

            if existing:
                for key, value in row.items():
                    setattr(existing, key, value)
            else:
                c = Company(**row)
                db.session.add(c)

            success_count += 1
        except Exception as e:
            errors.append(f'行解析失败: {str(e)}')

    # 更新所有订单的负责人
    update_all_orders_manager()
    db.session.commit()
    return success_count, errors


IMPORT_FUNCTIONS = {
    'delivery_schedule': import_delivery_schedule,
    'shipment': import_shipment,
    'factory_invoice': import_factory_invoice,
    'customer_invoice': import_customer_invoice,
    'company': import_company,
}


def import_excel(file, table_type):
    """
    统一导入入口。
    Args:
        file: Flask upload file object
        table_type: delivery_schedule/shipment/factory_invoice/customer_invoice/company
    Returns:
        (success_count, error_messages, saved_path)
    """
    if table_type not in IMPORT_FUNCTIONS:
        return 0, [f'未知表类型: {table_type}'], None

    # 保存文件
    filepath = _save_upload_file(file, table_type)

    # 导入
    func = IMPORT_FUNCTIONS[table_type]
    success, errors = func(filepath)

    # 记录系统日志
    log = SystemLog(
        action=f'import_{table_type}',
        operator='system',
        detail=f'导入文件: {os.path.basename(filepath)}, 成功: {success}, 失败: {len(errors)}'
    )
    db.session.add(log)
    db.session.commit()

    return success, errors, filepath
