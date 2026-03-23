import os
from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from flask_caching import Cache # Added Flask-Caching import
from flask_sqlalchemy import SQLAlchemy # Added SQLAlchemy import for global db object

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Initialize extensions globally
login_manager = LoginManager()
cache = Cache() # Initialized Cache globally

from app.models import db, User, InstitutionConfig, Category, Article, Department, InventoryMovement, StockAlert # Removed db from import as it's now global


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración de SECRET_KEY
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-12345')
    
    # Configuración Dinámica de Base de Datos
    # Prioridad: DATABASE_URL (Personalizado/Nube) > Motores Individuales > SQLite Default
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        engine = os.environ.get('DB_ENGINE', 'sqlite')
        db_user = os.environ.get('DB_USER', '')
        db_pass = os.environ.get('DB_PASSWORD', '')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '')
        db_name = os.environ.get('DB_NAME', 'inventory')
        
        if engine == 'mysql':
            port = f":{db_port}" if db_port else ""
            db_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}{port}/{db_name}"
        elif engine == 'postgresql':
            port = f":{db_port}" if db_port else ""
            db_url = f"postgresql://{db_user}:{db_pass}@{db_host}{port}/{db_name}"
        else:
            # Default SQLite
            instance_path = app.instance_path
            if not os.path.exists(instance_path):
                os.makedirs(instance_path)
            db_url = f'sqlite:///{os.path.join(instance_path, "inventory.sqlite")}'

    # Corrección común para SQLAlchemy 1.4+ con Postgres (heroku/render)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'img', 'logos')

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    login_manager.login_view = 'auth.login'
    # Register configurations context processor
    @app.context_processor
    def inject_config():
        from app.models import InstitutionConfig
        config = InstitutionConfig.query.first()
        return dict(config=config)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Importar y Registrar Blueprints (Módulos SGI)
    from app.blueprints.auth import auth as auth_bp
    from app.blueprints.dashboard import dashboard as dashboard_bp
    from app.blueprints.stock import stock as stock_bp
    from app.blueprints.admin import admin as admin_bp
    from app.blueprints.reports import reports as reports_bp
    from app.blueprints.api import api as api_bp
    from app.blueprints.legal import legal as legal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(legal_bp)
    
    # The 'main' blueprint is no longer needed or should be replaced by dashboard/auth
    # from app.routes import main as main_blueprint
    # app.register_blueprint(main_blueprint)
    
    with app.app_context():
        db.create_all()
        # Seed default admin and config if they don't exist
        if not User.query.filter_by(username='admin').first():
            # from werkzeug.security import generate_password_hash # Already imported at top
            user = User(username='admin', password=generate_password_hash('admin', method='pbkdf2:sha256'), is_admin=True)
            db.session.add(user)
        
        if not InstitutionConfig.query.first():
            config = InstitutionConfig()
            db.session.add(config)
            
        db.session.commit()

    return app
