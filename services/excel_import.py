import openpyxl
from app import db
from models import (DeliverySchedule, Shipment, FactoryInvoice,
                    CustomerInvoice, Company)


class ExcelImportService:
    """Excel 上传解析服务"""

    # 表名映射：中文表头 -> 数据库字段名
    DELIVERY_SCHEDULE_MAP = {
        'MRP控制者': 'mrp_controller',
        '销售订单号': 'sales_order_no',
        '销售订单行项目号': 'sales_order_line_no',
        '客户名称': 'customer_name',
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
        '客户名称': 'customer_name',
        '终端名称': 'terminal_name',
        '客户订单号': 'customer_order_no',
        '客户对应代码': 'customer_code',
        '物料名称': 'material_name',
        '合同数': 'contract_quantity',
        '本次送货数': 'delivery_quantity',
        '单据日期': 'document_date',
        '物流单号': 'logistics_no',
        '运输方式': 'transport_method',
        '快递单号': 'express_no',
        '箱数': 'box_count',
        '箱号': 'box_no',
    }

    FACTORY_INVOICE_MAP = {
        '售达方客户代码名称': 'customer_code_name',
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
        '出库日期': 'warehouse_date',
        '订单日期': 'order_date',
        '指定送货地址': 'delivery_address',
    }

    CUSTOMER_INVOICE_MAP = {
        '指定地点': 'designated_location',
        '订单号': 'order_no',
        '客户产品代码': 'customer_product_code',
        '规格': 'specification',
        '发货数': 'shipped_quantity',
        '发货日期': 'ship_date',
        '含税单价': 'price_incl_tax',
        '含税金额': 'amount_incl_tax',
    }

    COMPANY_MAP = {
        '公司名称': 'company_name',
        '收货地址': 'shipping_address',
        '负责人': 'manager',
        '联系人': 'contact_person',
        '线上联系方式': 'online_contact',
        '电话': 'phone',
    }

    TABLE_MAPS = {
        'delivery_schedule': DELIVERY_SCHEDULE_MAP,
        'shipment': SHIPMENT_MAP,
        'factory_invoice': FACTORY_INVOICE_MAP,
        'customer_invoice': CUSTOMER_INVOICE_MAP,
        'company': COMPANY_MAP,
    }

    TABLE_MODELS = {
        'delivery_schedule': DeliverySchedule,
        'shipment': Shipment,
        'factory_invoice': FactoryInvoice,
        'customer_invoice': CustomerInvoice,
        'company': Company,
    }

    @classmethod
    def parse_excel(cls, file_path, table_type):
        """解析Excel文件并导入数据库

        Args:
            file_path: Excel文件路径
            table_type: 表类型 (delivery_schedule/shipment/factory_invoice/customer_invoice/company)

        Returns:
            (success_count, error_messages)
        """
        if table_type not in cls.TABLE_MAPS:
            return 0, [f'未知表类型: {table_type}']

        wb = openpyxl.load_workbook(file_path, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        wb.close()

        if not rows:
            return 0, ['Excel文件为空']

        # 第一行为表头，建立映射
        header = [str(cell).strip() if cell else '' for cell in rows[0]]
        field_map = cls.TABLE_MAPS[table_type]
        col_mapping = {}
        for idx, col_name in enumerate(header):
            if col_name in field_map:
                col_mapping[idx] = field_map[col_name]

        if not col_mapping:
            return 0, [f'未匹配到有效列名，请检查表头。期望列名: {list(field_map.keys())}']

        Model = cls.TABLE_MODELS[table_type]
        success_count = 0
        errors = []

        # 数据行从第2行开始
        for row_idx, row in enumerate(rows[1:], start=2):
            try:
                data = {}
                for col_idx, field_name in col_mapping.items():
                    value = row[col_idx] if col_idx < len(row) else None
                    data[field_name] = str(value).strip() if value is not None else None

                record = Model(**data)
                db.session.add(record)
                success_count += 1
            except Exception as e:
                errors.append(f'第{row_idx}行解析失败: {str(e)}')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return 0, [f'数据库保存失败: {str(e)}']

        return success_count, errors
