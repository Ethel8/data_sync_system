import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 数据库
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'db', 'data', 'app.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 上传
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 提醒（天数）
REMINDER_PICKUP_DAYS_BEFORE = 3       # 提货提前提醒天数
REMINDER_PAYMENT_DAYS_BEFORE = 7      # 结款提前提醒天数

# Excel 导入允许的表类型
ALLOWED_TABLES = ['delivery_schedule', 'shipment', 'invoice_factory', 'invoice_customer', 'company']

# 日志
LOG_DIR = os.path.join(BASE_DIR, 'logs')
