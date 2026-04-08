from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, InstitutionConfig
from app.decorators import admin_required
from sqlalchemy import text
import platform
import psutil
import sys
import time
import os
from datetime import datetime
from app.utils.env_manager import set_env_variable, get_db_config

admin = Blueprint('admin', __name__)

@admin.route('/admin/config', methods=['GET', 'POST'])
@admin_required
def config():
    config = InstitutionConfig.query.first()
    if not config:
        config = InstitutionConfig()
        db.session.add(config)
        db.session.commit()
    
    if request.method == 'POST':
        config.name = request.form.get('name')
        config.commercial_name = request.form.get('commercial_name')
        config.rif = request.form.get('rif')
        config.address = request.form.get('address')
        config.city = request.form.get('city')
        config.state = request.form.get('state')
        config.municipality = request.form.get('municipality')
        config.parish = request.form.get('parish')
        config.phone = request.form.get('phone')
        config.email = request.form.get('email')
        
        config.telegram_bot_token = request.form.get('telegram_bot_token')
        config.telegram_chat_id = request.form.get('telegram_chat_id')
        config.api_key = request.form.get('api_key')
        
        logo = request.files.get('logo')
        if logo and logo.filename:
            filename = secure_filename(logo.filename)
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            logo.save(logo_path)
            config.logo_filename = filename
            
        db.session.commit()

        # Configuración de Base de Datos (Persistida en .env)
        db_engine = request.form.get('db_engine')
        if db_engine:
            set_env_variable('DB_ENGINE', db_engine)
            set_env_variable('DB_HOST', request.form.get('db_host', 'localhost'))
            set_env_variable('DB_PORT', request.form.get('db_port', ''))
            set_env_variable('DB_USER', request.form.get('db_user', ''))
            set_env_variable('DB_PASSWORD', request.form.get('db_password', ''))
            set_env_variable('DB_NAME', request.form.get('db_name', 'inventory'))
            flash('Configuración de Base de Datos guardada. El sistema puede requerir un reinicio para aplicar los cambios.', 'warning')

        flash('Configuración de SGI-Core actualizada.', 'success')
        return redirect(url_for('admin.config'))
        
    db_config = get_db_config()
    return render_template('config.html', config=config, db_config=db_config)

@admin.route('/admin/status')
@admin_required
def status():
    # System Information
    sys_info = {
        'os': platform.system(),
        'os_release': platform.release(),
        'os_version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': sys.version,
        'node_name': platform.node(),
    }
    
    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=None)
    cpu_count = psutil.cpu_count()
    
    # Memory usage
    memory = psutil.virtual_memory()
    memory_info = {
        'total': round(memory.total / (1024**3), 2),
        'available': round(memory.available / (1024**3), 2),
        'used': round(memory.used / (1024**3), 2),
        'percent': memory.percent
    }
    
    # Disk usage
    disk = psutil.disk_usage('/')
    disk_info = {
        'total': round(disk.total / (1024**3), 2),
        'used': round(disk.used / (1024**3), 2),
        'free': round(disk.free / (1024**3), 2),
        'percent': disk.percent
    }
    
    # Boot time
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    # Database status
    db_status = "Operacional"
    try:
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        db_status = f"Error: {str(e)}"

    return render_template('core_status.html', 
                           sys_info=sys_info,
                           cpu_usage=cpu_usage,
                           cpu_count=cpu_count,
                           memory_info=memory_info,
                           disk_info=disk_info,
                           uptime=str(uptime).split('.')[0],
                           db_status=db_status)
@admin.route('/admin/users')
@admin_required
def list_users():
    from app.models import User
    page = request.args.get('page', 1, type=int)
    # Paginación (A3)
    pagination = User.query.paginate(page=page, per_page=15, error_out=False)
    return render_template('users.html', pagination=pagination, users=pagination.items)

@admin.route('/admin/users/add', methods=['POST'])
@admin_required
def add_user():
    from app.models import User
    from werkzeug.security import generate_password_hash
    
    username = request.form.get('username')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    role = request.form.get('role', 'Operador')
    is_admin = True if role == 'Administrador' else False
    
    if len(password) < 8:
        flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
        return redirect(url_for('admin.list_users'))
    
    if User.query.filter_by(username=username).first():
        flash('El nombre de usuario ya existe.', 'danger')
    else:
        new_user = User(
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            full_name=full_name,
            email=email,
            role=role,
            is_admin=is_admin
        )
        db.session.add(new_user)
        db.session.commit()
        flash(f'Usuario {username} creado exitosamente.', 'success')
        
    return redirect(url_for('admin.list_users'))

@admin.route('/admin/users/edit/<int:user_id>', methods=['POST'])
@admin_required
def edit_user(user_id):
    from app.models import User
    from werkzeug.security import generate_password_hash
    
    user = User.query.get_or_404(user_id)
    user.full_name = request.form.get('full_name')
    user.email = request.form.get('email')
    user.phone = request.form.get('phone')
    user.role = request.form.get('role')
    user.is_admin = True if user.role == 'Administrador' else False
    
    new_password = request.form.get('password')
    if new_password:
        if len(new_password) < 8:
            flash('La nueva contraseña debe tener al menos 8 caracteres.', 'danger')
            return redirect(url_for('admin.list_users'))
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        
    db.session.commit()
    flash(f'Datos de {user.username} actualizados.', 'success')
    return redirect(url_for('admin.list_users'))

@admin.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    from app.models import User
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado.', 'success')
        
    return redirect(url_for('admin.list_users'))
