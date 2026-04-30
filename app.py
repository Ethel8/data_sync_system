from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from models import (DeliverySchedule, Shipment, FactoryInvoice,
                            CustomerInvoice, Company, Order, OrderLog, SystemLog)
        db.create_all()

    from routes.dashboard import dashboard_bp
    from routes.order import order_bp
    from routes.upload import upload_bp
    from routes.anomaly import anomaly_bp
    from routes.reminder import reminder_bp
    from routes.analysis import analysis_bp
    from routes.company import company_bp
    from routes.payment import payment_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(order_bp, url_prefix='/order')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(anomaly_bp, url_prefix='/anomaly')
    app.register_blueprint(reminder_bp, url_prefix='/reminder')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(company_bp, url_prefix='/company')
    app.register_blueprint(payment_bp, url_prefix='/payment')

    return app
