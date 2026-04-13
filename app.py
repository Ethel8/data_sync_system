import os
from flask import Flask, render_template
from config import Config
from db.database import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # 确保目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'db', 'data'), exist_ok=True)

    # 初始化数据库
    init_db(app)

    # 注册蓝图
    from routes.order_routes import bp as order_bp
    from routes.upload_routes import bp as upload_bp
    from routes.analysis_routes import bp as analysis_bp
    from routes.company_routes import bp as company_bp
    from routes.master_routes import bp as master_bp

    app.register_blueprint(order_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(master_bp)

    # 首页
    @app.route('/')
    def index():
        from models.order import Order, OrderStatus
        from services.reminder_service import get_all_reminders
        stats = {
            'total': Order.query.count(),
            'normal': Order.query.filter_by(status=OrderStatus.NORMAL).count(),
            'anomaly': Order.query.filter_by(status=OrderStatus.ANOMALY).count(),
            'completed': Order.query.filter_by(status=OrderStatus.COMPLETED).count(),
        }
        reminders = get_all_reminders()
        return render_template('index.html', stats=stats, reminders=reminders)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
