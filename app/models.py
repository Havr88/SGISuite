from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) # hashed
    is_admin = db.Column(db.Boolean, default=False)
    full_name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(50), default="Operador")

class InstitutionConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, default="Nombre de Institución")
    commercial_name = db.Column(db.String(200), nullable=False, default="Siglas o Nombre Comercial")
    rif = db.Column(db.String(50), nullable=False, default="J-00000000-0")
    address = db.Column(db.String(300), nullable=False, default="Dirección Institucional Principal")
    city = db.Column(db.String(100), nullable=False, default="Ciudad")
    state = db.Column(db.String(100), nullable=False, default="Estado")
    municipality = db.Column(db.String(100), nullable=True, default="Municipio")
    parish = db.Column(db.String(100), nullable=True, default="Parroquia")
    phone = db.Column(db.String(100), nullable=False, default="0000-0000000")
    email = db.Column(db.String(100), nullable=False, default="correo@institucion.com")
    logo_filename = db.Column(db.String(200), nullable=True)
    
    # PDF config
    margin_top = db.Column(db.Float, default=2.5)
    margin_bottom = db.Column(db.Float, default=2.5)
    font_family = db.Column(db.String(50), default="Arial")
    font_size = db.Column(db.Integer, default=11)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    abbreviation = db.Column(db.String(20), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False) # Conteo, Empaque, Masa, Volumen, Longitud
    description = db.Column(db.String(200), nullable=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    # Unit Configuration
    base_unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    purchase_unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=True)
    conversion_factor = db.Column(db.Float, default=1.0) # 1 Purchase Unit = X Base Units
    
    # Relationships
    base_unit = db.relationship('Unit', foreign_keys=[base_unit_id])
    purchase_unit = db.relationship('Unit', foreign_keys=[purchase_unit_id])

    location = db.Column(db.String(150), nullable=True)
    min_stock = db.Column(db.Float, default=10.0)
    max_stock = db.Column(db.Float, default=100.0)
    current_stock = db.Column(db.Float, default=0.0)
    observations = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Activo")
    unit_cost = db.Column(db.Float, default=0.0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('articles', lazy=True))

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.String(300), nullable=True)
    manager_name = db.Column(db.String(150), nullable=True)
    manager_role = db.Column(db.String(50), nullable=True)
    manager_date_from = db.Column(db.Date, nullable=True)
    manager_date_to = db.Column(db.Date, nullable=True)

class InventoryMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movement_type = db.Column(db.String(10), nullable=False) # 'IN' or 'OUT'
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    article = db.relationship('Article', backref=db.backref('movements', lazy=True))
    quantity = db.Column(db.Float, nullable=False)
    movement_unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=True)
    movement_unit = db.relationship('Unit')
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('movements', lazy=True))
    
    # For 'OUT' (Entregas)
    receiver_name = db.Column(db.String(150), nullable=True)
    receiver_cedula = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    department = db.relationship('Department', backref=db.backref('movements', lazy=True))
    observations = db.Column(db.Text, nullable=True)
    document_filename = db.Column(db.String(250), nullable=True)

class StockAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    article = db.relationship('Article', backref=db.backref('alerts', lazy=True))
    alert_date = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="Pendiente") # 'Pendiente', 'Resuelta'
