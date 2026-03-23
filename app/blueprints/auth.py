from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, db
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard.index'))
        flash('Credenciales incorrectas.', 'danger')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        
        # Opcional: Cambiar contraseña si se proporciona
        new_password = request.form.get('new_password')
        if new_password:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            
        db.session.commit()
        flash('Perfil actualizado exitosamente.', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('profile.html', user=current_user)
