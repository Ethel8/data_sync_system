from flask import Blueprint, render_template, request
from db.database import db
from sqlalchemy import text

bp = Blueprint('master', __name__, url_prefix='/master')

# 字段分组定义
FIELD_GROUPS = {
    'delivery': [
        {'key': 'sales_order_no', 'label': '销售订单号'},
        {'key': 'sales_order_line', 'label': '行项目号'},
        {'key': 'customer_name', 'label': '客户名称'},
        {'key': 'ship_to_name', 'label': '送达方名称'},
        {'key': 'create_date', 'label': '创建日期'},
        {'key': 'customer_contract_no', 'label': '客户合同号'},
        {'key': 'customer_material_code', 'label': '客户物料代码'},
        {'key': 'falah_code', 'label': '法拉外码'},
        {'key': 'order_quantity', 'label': '订单数量'},
        {'key': 'unshipped_qty', 'label': '未出库数量'},
        {'key': 'review_delivery_date', 'label': '订单评审交期'},
        {'key': 'order_status_sap', 'label': 'SAP下达状态'},
        {'key': 'planned_inbound_date', 'label': '计划应入库日期'},
        {'key': 'customer_required_date', 'label': '客户要求交期'},
        {'key': 'unstocked_qty', 'label': '未入库数量'},
        {'key': 'stocked_qty', 'label': '已入库数量'},
        {'key': 'shipped_qty', 'label': '已出库数量'},
        {'key': 'order_line_remark', 'label': '行备注'},
        {'key': 'customer_line', 'label': '客户项次'},
    ],
    'shipment': [
        {'key': 'delivery_no', 'label': '送货单号'},
        {'key': 'terminal_name', 'label': '终端名称'},
        {'key': 'customer_code', 'label': '客户对应代码'},
        {'key': 'material_name', 'label': '物料名称'},
        {'key': 'contract_qty', 'label': '合同数'},
        {'key': 'shipment_delivery_qty', 'label': '本次送货数'},
        {'key': 'document_date', 'label': '单据日期'},
        {'key': 'logistics_no', 'label': '物流单号'},
        {'key': 'transport_method', 'label': '运输方式'},
        {'key': 'express_no', 'label': '快递单号'},
        {'key': 'box_count', 'label': '箱数'},
        {'key': 'box_no', 'label': '箱号'},
    ],
    'invoice': [
        {'key': 'customer_code_name', 'label': '售达方代码名称'},
        {'key': 'customer_po_no', 'label': '客户采购订单号'},
        {'key': 'outbound_no', 'label': '出库单号'},
        {'key': 'invoice_qty', 'label': '开票数量'},
        {'key': 'outbound_qty', 'label': '出库数量'},
        {'key': 'uninvoiced_qty', 'label': '未开票数量'},
        {'key': 'unit_price_excl_tax', 'label': '不含税单价'},
        {'key': 'unit_price_incl_tax', 'label': '含税单价'},
        {'key': 'uninvoiced_amount_excl_tax', 'label': '未开票不含税金额'},
        {'key': 'uninvoiced_amount_incl_tax', 'label': '未开票价税合计'},
        {'key': 'outbound_date', 'label': '出库日期'},
        {'key': 'invoice_order_date', 'label': '订单日期(开票)'},
        {'key': 'delivery_address', 'label': '指定送货地址'},
        {'key': 'delivery_location', 'label': '指定地点(客户)'},
        {'key': 'customer_product_code', 'label': '客户产品代码'},
        {'key': 'specification', 'label': '规格'},
        {'key': 'inv_shipment_qty', 'label': '发货数(客户开票)'},
        {'key': 'inv_shipment_date', 'label': '发货日期(客户)'},
        {'key': 'inv_amount', 'label': '含税金额'},
    ],
    'company': [
        {'key': 'shipping_address', 'label': '收货地址'},
        {'key': 'company_manager', 'label': '负责人'},
        {'key': 'company_contact_person', 'label': '联系人'},
        {'key': 'company_online_contact', 'label': '线上联系方式'},
        {'key': 'company_phone', 'label': '电话'},
    ],
    'status': [
        {'key': 'status', 'label': '订单状态'},
        {'key': 'order_primary_status', 'label': '订单一级状态'},
        {'key': 'order_secondary_status', 'label': '订单二级状态'},
    ],
}

ALL_FIELDS = {f['key']: f['label'] for group in FIELD_GROUPS.values() for f in group}


@bp.route('/')
def master_list():
    keyword = request.args.get('keyword', '')
    fields_param = request.args.get('fields', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # 解析选中字段
    if fields_param:
        selected_fields = [f.strip() for f in fields_param.split(',') if f.strip() in ALL_FIELDS]
    else:
        # 默认展示核心字段
        selected_fields = [
            'sales_order_no', 'customer_name',
            'order_primary_status', 'order_secondary_status',
        ]

    # 构建查询
    col_str = ', '.join(selected_fields) if selected_fields else '*'
    sql = f"SELECT {col_str} FROM master_view"
    params = {}
    if keyword:
        sql += " WHERE sales_order_no LIKE :kw OR customer_name LIKE :kw OR customer_material_code LIKE :kw OR falah_code LIKE :kw"
        params['kw'] = f'%{keyword}%'

    sql += " ORDER BY create_date DESC NULLS LAST"

    # 分页
    count_sql = sql.replace(f"SELECT {col_str}", "SELECT COUNT(*)")
    total = db.session.execute(text(count_sql), params).scalar()
    offset = (page - 1) * per_page
    sql += f" LIMIT {per_page} OFFSET {offset}"

    result = db.session.execute(text(sql), params)
    rows = [dict(zip(result.keys(), row)) for row in result.fetchall()]
    total_pages = max(1, (total + per_page - 1) // per_page)

    # 字段标签映射（用于表头显示中文名）
    selected_labels = [ALL_FIELDS.get(f, f) for f in selected_fields]

    return render_template('master/list.html',
                           rows=rows,
                           selected_fields=selected_fields,
                           selected_labels=selected_labels,
                           field_groups=FIELD_GROUPS,
                           keyword=keyword,
                           page=page,
                           total_pages=total_pages,
                           total=total,
                           fields_param=fields_param)
