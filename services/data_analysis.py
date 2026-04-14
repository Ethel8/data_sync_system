from app import db
from models import (Order, DeliverySchedule, Shipment, FactoryInvoice,
                    CustomerInvoice)


class DataAnalysisService:
    """统计分析服务 - 对账表和欠款表（实时聚合计算）"""

    @staticmethod
    def get_reconciliation():
        """生成对账表 - 基于业务表实时聚合"""
        # 关联发货表和开票表数据，计算利润
        results = db.session.query(
            Shipment.customer_name,
            Shipment.customer_order_no,
            Shipment.customer_code,
            Shipment.material_name,
            Shipment.delivery_quantity,
            Shipment.document_date,
        ).all()

        reconciliation = []
        for row in results:
            item = {
                'company_name': row.customer_name or '',
                'customer_order_no': row.customer_order_no or '',
                'customer_code': row.customer_code or '',
                'fara_external_code': row.material_name or '',
                'shipment_quantity': row.delivery_quantity or '',
                'shipment_date': row.document_date or '',
                'buy_price_excl_tax': '',
                'buy_total': '',
                'sell_price': '',
                'sell_total': '',
                'profit_rate': '',
                'profit': '',
            }

            # 查找对应的工厂开票信息获取买入价
            invoice = FactoryInvoice.query.filter(
                FactoryInvoice.sales_order_no == row.customer_order_no
            ).first()
            if invoice:
                item['buy_price_excl_tax'] = invoice.price_excl_tax or ''
                try:
                    qty = float(row.delivery_quantity or 0)
                    price = float(invoice.price_excl_tax or 0)
                    item['buy_total'] = round(qty * price, 2)
                except (ValueError, TypeError):
                    pass

            # 查找对应的客户开票信息获取卖出价
            c_invoice = CustomerInvoice.query.filter(
                CustomerInvoice.order_no == row.customer_order_no
            ).first()
            if c_invoice:
                item['sell_price'] = c_invoice.price_incl_tax or ''
                try:
                    qty = float(row.delivery_quantity or 0)
                    price = float(c_invoice.price_incl_tax or 0)
                    item['sell_total'] = round(qty * price, 2)
                except (ValueError, TypeError):
                    pass

            # 计算利润
            try:
                buy = float(item['buy_total'] or 0)
                sell = float(item['sell_total'] or 0)
                profit = round(sell - buy, 2)
                item['profit'] = profit
                if buy > 0:
                    item['profit_rate'] = f'{round(profit / buy * 100, 2)}%'
            except (ValueError, TypeError):
                pass

            reconciliation.append(item)

        return reconciliation

    @staticmethod
    def get_arrears():
        """生成欠款表 - 基于业务表实时聚合"""
        # 查找待结款和异常未结款的订单
        pending_orders = Order.query.join(DeliverySchedule).filter(
            Order.primary_status.in_(['正常', '异常']),
        ).all()

        arrears = []
        for order in pending_orders:
            ds = order.delivery_schedule
            if not ds:
                continue

            item = {
                'company_name': ds.customer_name or '',
                'customer_order_no': ds.sales_order_no or '',
                'customer_code': ds.customer_material_code or '',
                'fara_external_code': ds.fara_external_code or '',
                'receivable': '',
                'paid': '',
                'arrears_amount': '',
            }

            # 查找对应的开票信息获取应收款项
            invoice = FactoryInvoice.query.filter(
                FactoryInvoice.sales_order_no == ds.sales_order_no
            ).first()
            if invoice:
                item['receivable'] = invoice.uninvoiced_amount_incl_tax or ''
                try:
                    receivable = float(invoice.uninvoiced_amount_incl_tax or 0)
                    item['arrears_amount'] = receivable
                except (ValueError, TypeError):
                    pass

            if order.primary_status == '异常':
                item['status'] = f'异常/{order.secondary_status}'
            else:
                item['status'] = f'{order.primary_status}/{order.secondary_status}'

            arrears.append(item)

        return arrears
