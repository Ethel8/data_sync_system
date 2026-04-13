from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """初始化数据库，建表 + 创建视图"""
    db.init_app(app)
    with app.app_context():
        from models.order import Order
        from models.company import Company
        from models.log import OperationLog
        from models.delivery_schedule import DeliverySchedule
        from models.shipment import Shipment
        from models.invoice_factory import InvoiceFactory
        from models.invoice_customer import InvoiceCustomer
        db.create_all()

        # 创建总表视图
        from db.master_view import create_master_view
        from sqlalchemy import text
        create_master_view(db.engine)
