from datetime import datetime, date
from app import db
from models import Order, DeliverySchedule, Shipment, CustomerInvoice, FactoryInvoice, Company


def recalculate_order_status(order):
    """
    订单主表每次更新后调用，重算订单进度、开票状态、订单状态。
    """
    _recalculate_order_progress(order)
    _recalculate_invoice_status(order)
    _detect_anomaly(order)
    _recalculate_order_status_final(order)
    db.session.add(order)


def _safe_float(val):
    """安全转换为 float"""
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _safe_date(val):
    """安全转换为 date 对象"""
    if not val:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    # 尝试解析字符串格式
    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y年%m月%d日']:
        try:
            return datetime.strptime(str(val).strip(), fmt).date()
        except ValueError:
            continue
    return None


def _recalculate_order_progress(order):
    """Task 2.1 - 重算订单进度"""
    ds = DeliverySchedule.query.filter_by(
        sales_order_no=order.sales_order_no,
        fara_external_code=order.fara_external_code,
        order_quantity=order.order_quantity
    ).first()

    if ds is None:
        return

    warehoused = _safe_float(ds.warehoused_quantity)
    shipped = _safe_float(ds.shipped_quantity)
    unshipped = _safe_float(ds.unshipped_quantity)
    qty = _safe_float(ds.order_quantity)

    # 未出库数量 = 订单数量 - 已出库数量
    # 但也用交期表原始的未出库数量
    # 已入库数量 == 订单数量 且 已入库数量 == 未出库数量 → 待提货
    if warehoused >= qty and qty > 0:
        # 已全部入库
        if shipped >= qty:
            order.order_progress = '待结款'
        elif shipped > 0:
            order.order_progress = '部分发货'
        elif unshipped >= qty:
            # 全部入库且全部未出库
            order.order_progress = '待提货'
        else:
            order.order_progress = '部分发货'
    elif warehoused > 0:
        order.order_progress = '生产中'
    else:
        order.order_progress = '生产中'

    # 只有已结款状态才保留
    if order.order_progress == '已结款':
        pass  # 由结款逻辑设置，不覆盖


def _recalculate_invoice_status(order):
    """Task 2.2 - 重算公司开票和客户开票状态"""
    qty = _safe_float(order.order_quantity)
    if qty <= 0:
        return

    # 公司开票
    fi_qty = _safe_float(order.factory_invoice_quantity)
    if fi_qty <= 0:
        order.factory_invoice_status = '未开票'
    elif fi_qty < qty:
        order.factory_invoice_status = '部分开票'
    elif fi_qty == qty:
        order.factory_invoice_status = '已开票'
    else:
        # 开票数量 > 订单数量 → 报错（通过日志记录，不阻断）
        from models import SystemLog
        log = SystemLog(
            action='ERROR',
            operator='system',
            detail=f'订单 {order.sales_order_no}/{order.fara_external_code} 公司开票数量({fi_qty})超过订单数量({qty})'
        )
        db.session.add(log)

    # 客户开票
    ci_qty = _safe_float(order.customer_invoice_quantity)
    if ci_qty <= 0:
        order.customer_invoice_status = '未开票'
    elif ci_qty < qty:
        order.customer_invoice_status = '部分开票'
    elif ci_qty == qty:
        order.customer_invoice_status = '已开票'
    else:
        from models import SystemLog
        log = SystemLog(
            action='ERROR',
            operator='system',
            detail=f'订单 {order.sales_order_no}/{order.fara_external_code} 客户开票数量({ci_qty})超过订单数量({qty})'
        )
        db.session.add(log)


def _detect_anomaly(order):
    """Task 2.4 - 异常检测"""
    today = date.today()

    # 只有正常状态的订单才检测异常
    if order.order_status != '正常':
        return

    # 超时未提货：订单进度=="待提货" 且 当前日期 > 交期表的订单评审交期（同天不算）
    if order.order_progress == '待提货':
        ds = DeliverySchedule.query.filter_by(
            sales_order_no=order.sales_order_no,
            fara_external_code=order.fara_external_code,
            order_quantity=order.order_quantity
        ).first()
        if ds:
            review_date = _safe_date(ds.order_review_date)
            if review_date and today > review_date:
                order.order_progress = '超时未提货'

    # 超时未结款：订单进度=="待结款" 且 发货日期已过1个月
    if order.order_progress == '待结款':
        ship_d = _safe_date(order.ship_date)
        if ship_d:
            from dateutil.relativedelta import relativedelta
            one_month_later = ship_d + relativedelta(months=1)
            if today >= one_month_later:
                order.order_progress = '超时未结款'


def _recalculate_order_status_final(order):
    """Task 2.3/2.6 - 重算订单状态（正常/异常/完结/退单）"""
    # 退单只由手动设置，不自动变更
    if order.order_status == '退单':
        return

    progress = order.order_progress or ''
    fi_status = order.factory_invoice_status or ''
    ci_status = order.customer_invoice_status or ''

    # 完结条件
    if progress == '已结款' and fi_status == '已开票' and ci_status == '已开票':
        order.order_status = '完结'
        return

    # 异常条件
    anomaly_progress = ['超时未提货', '超时未结款', '入库后退货', '开票后退货']
    if progress in anomaly_progress or fi_status == '需退票' or ci_status == '需退票':
        order.order_status = '异常'
        return

    # 正常条件
    normal_progress = ['生产中', '待提货', '部分发货', '待结款', '已结款']
    normal_invoice = ['未开票', '部分开票', '已开票']
    if progress in normal_progress and fi_status in normal_invoice and ci_status in normal_invoice:
        order.order_status = '正常'


def update_all_orders_manager():
    """
    客户明细表更新后，更新所有订单主表的负责人。
    """
    companies = Company.query.all()
    company_map = {c.ship_to_name: c.manager for c in companies if c.ship_to_name}

    orders = Order.query.all()
    for order in orders:
        if order.ship_to_name and order.ship_to_name in company_map:
            if order.manager != company_map[order.ship_to_name]:
                order.manager = company_map[order.ship_to_name]
                db.session.add(order)
