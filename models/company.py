from db.database import db
from datetime import datetime


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False, comment='公司名称')
    shipping_address = db.Column(db.String(256), comment='收货地址')
    manager = db.Column(db.String(64), comment='负责人')
    contact_person = db.Column(db.String(64), comment='联系人')
    online_contact = db.Column(db.String(128), comment='线上联系方式')
    phone = db.Column(db.String(32), comment='电话')
    remark = db.Column(db.String(256), comment='备注')

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
