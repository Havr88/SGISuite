import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, Category, Article, Department, InventoryMovement, InstitutionConfig, Unit, StockAlert
from datetime import datetime

stock = Blueprint('stock', __name__)

@stock.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        next_url = request.form.get('next', url_for('stock.categories'))
        if name:
            existing = Category.query.filter(db.func.lower(Category.name) == name.lower()).first()
            if existing:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': f'Ya existe una categoría llamada "{existing.name}".'})
                flash(f'Ya existe una categoría llamada "{existing.name}".', 'danger')
            else:
                new_cat = Category(name=name, description=description)
                db.session.add(new_cat)
                db.session.commit()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': 'Categoría agregada exitosamente.'})
                flash('Categoría agregada exitosamente.', 'success')
        return redirect(next_url)
        
    cats = Category.query.all()
    return render_template('categories.html', categories=cats)

@stock.route('/departments', methods=['GET', 'POST'])
@login_required
def departments():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        manager_name = request.form.get('manager_name', '').strip()
        manager_role = request.form.get('manager_role')
        manager_date_from = request.form.get('manager_date_from')
        manager_date_to = request.form.get('manager_date_to')
        next_url = request.form.get('next', url_for('stock.departments'))
        
        d_from = None
        d_to = None
        if manager_date_from:
            d_from = datetime.strptime(manager_date_from, '%Y-%m-%d').date()
        if manager_date_to:
            d_to = datetime.strptime(manager_date_to, '%Y-%m-%d').date()

        if name:
            existing = Department.query.filter(db.func.lower(Department.name) == name.lower()).first()
            if existing:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': f'Ya existe un departamento llamado "{existing.name}".'})
                flash(f'Ya existe un departamento llamado "{existing.name}".', 'danger')
            else:
                new_dep = Department(
                    name=name, description=description,
                    manager_name=manager_name, manager_role=manager_role,
                    manager_date_from=d_from, manager_date_to=d_to
                )
                db.session.add(new_dep)
                db.session.commit()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': 'Departamento agregado exitosamente.'})
                flash('Departamento agregado exitosamente.', 'success')
        return redirect(next_url)
        
    deps = Department.query.all()
    return render_template('departments.html', departments=deps)

@stock.route('/categories/edit/<int:id>', methods=['POST'])
@login_required
def edit_category(id):
    cat = Category.query.get_or_404(id)
    new_name = request.form.get('name', '').strip()
    if new_name:
        collision = Category.query.filter(
            db.func.lower(Category.name) == new_name.lower(),
            Category.id != id
        ).first()
        if collision:
            flash(f'Ya existe otra categoría llamada "{collision.name}".', 'danger')
            return redirect(url_for('stock.categories'))
        cat.name = new_name
    cat.description = request.form.get('description', '').strip()
    db.session.commit()
    flash('Categoría actualizada.', 'success')
    return redirect(url_for('stock.categories'))

@stock.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    cat = Category.query.get_or_404(id)
    if cat.articles:
        flash('No se puede eliminar: Esta categoría tiene artículos asociados.', 'danger')
    else:
        db.session.delete(cat)
        db.session.commit()
        flash('Categoría eliminada.', 'success')
    return redirect(url_for('stock.categories'))

@stock.route('/departments/edit/<int:id>', methods=['POST'])
@login_required
def edit_department(id):
    dep = Department.query.get_or_404(id)
    new_name = request.form.get('name', '').strip()
    if new_name:
        collision = Department.query.filter(
            db.func.lower(Department.name) == new_name.lower(),
            Department.id != id
        ).first()
        if collision:
            flash(f'Ya existe otro departamento llamado "{collision.name}".', 'danger')
            return redirect(url_for('stock.departments'))
        dep.name = new_name
    dep.description = request.form.get('description', '').strip()
    dep.manager_name = request.form.get('manager_name', '').strip()
    dep.manager_role = request.form.get('manager_role')
    
    m_from = request.form.get('manager_date_from')
    m_to = request.form.get('manager_date_to')
    if m_from:
        try:
            dep.manager_date_from = datetime.strptime(m_from, '%Y-%m-%d').date()
        except: pass
    if m_to:
        try:
            dep.manager_date_to = datetime.strptime(m_to, '%Y-%m-%d').date()
        except: pass
    
    db.session.commit()
    flash('Departamento actualizado.', 'success')
    return redirect(url_for('stock.departments'))

@stock.route('/departments/delete/<int:id>', methods=['POST'])
@login_required
def delete_department(id):
    dep = Department.query.get_or_404(id)
    if dep.movements:
        flash('No se puede eliminar: Este departamento tiene movimientos de inventario registrados.', 'danger')
    else:
        db.session.delete(dep)
        db.session.commit()
        flash('Departamento eliminado.', 'success')
    return redirect(url_for('stock.departments'))


@stock.route('/articles')
@login_required
def articles():
    page = request.args.get('page', 1, type=int)
    # Paginación (A3)
    pagination = Article.query.paginate(page=page, per_page=15, error_out=False)
    categories_list = Category.query.all()
    units_list = Unit.query.all()
    return render_template('articles.html', pagination=pagination, articles=pagination.items, categories=categories_list, units=units_list)

@stock.route('/articles/add', methods=['POST'])
@login_required
def add_article():
    name = request.form.get('name', '').strip()
    category_id = request.form.get('category_id')
    base_unit_id = request.form.get('base_unit_id', type=int)
    purchase_unit_id = request.form.get('purchase_unit_id', type=int)
    conversion_factor = request.form.get('conversion_factor', 1.0, type=float)
    location = request.form.get('location', '').strip()
    min_stock = request.form.get('min_stock', 10.0, type=float)
    max_stock = request.form.get('max_stock', 100.0, type=float)
    unit_cost = request.form.get('unit_cost', 0.0, type=float)
    observations = request.form.get('observations', '').strip()
    next_url = request.form.get('next', url_for('stock.articles'))
    
    if name and category_id and base_unit_id:
        existing = Article.query.filter(
            db.func.lower(Article.name) == name.lower(),
            Article.category_id == category_id
        ).first()
        if existing:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Ya existe un artículo llamado "{existing.name}" en esa categoría.'})
            flash(f'Ya existe un artículo llamado "{existing.name}" en esa categoría.', 'danger')
        else:
            article = Article(
                name=name, category_id=category_id, 
                base_unit_id=base_unit_id,
                purchase_unit_id=purchase_unit_id,
                conversion_factor=conversion_factor,
                location=location, min_stock=min_stock, max_stock=max_stock,
                current_stock=0.0, observations=observations,
                unit_cost=unit_cost
            )
            db.session.add(article)
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Artículo agregado exitosamente.'})
            flash('Artículo agregado exitosamente.', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios (Nombre, Categoría y Unidad Base).'})
        flash('Faltan datos obligatorios (Nombre, Categoría y Unidad Base).', 'danger')
    return redirect(next_url)

@stock.route('/articles/edit/<int:id>', methods=['POST'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    category_id = request.form.get('category_id')
    base_unit_id = request.form.get('base_unit_id', type=int)
    purchase_unit_id = request.form.get('purchase_unit_id', type=int)
    conversion_factor = request.form.get('conversion_factor', 1.0, type=float)
    location = request.form.get('location', '').strip()
    min_stock = request.form.get('min_stock', 10.0, type=float)
    max_stock = request.form.get('max_stock', 100.0, type=float)
    unit_cost = request.form.get('unit_cost', 0.0, type=float)
    status = request.form.get('status', 'Activo').strip()
    observations = request.form.get('observations', '').strip()

    if name and category_id and base_unit_id:
        existing = Article.query.filter(
            db.func.lower(Article.name) == name.lower(),
            Article.category_id == category_id,
            Article.id != id
        ).first()
        if existing:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Ya existe un artículo llamado "{existing.name}" en esa categoría.'})
            flash(f'Ya existe un artículo llamado "{existing.name}" en esa categoría.', 'danger')
        else:
            article.name = name
            article.category_id = category_id
            article.base_unit_id = base_unit_id
            article.purchase_unit_id = purchase_unit_id
            article.conversion_factor = conversion_factor
            article.location = location
            article.min_stock = min_stock
            article.max_stock = max_stock
            article.unit_cost = unit_cost
            article.status = status
            article.observations = observations
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Artículo actualizado exitosamente.'})
            flash('Artículo actualizado exitosamente.', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Faltan datos obligatorios (Nombre, Categoría y Unidad Base).'})
        flash('Faltan datos obligatorios (Nombre, Categoría, y Unidad Base).', 'danger')

    return redirect(url_for('stock.articles'))

@stock.route('/inventory/in', methods=['GET', 'POST'])
@login_required
def inventory_in():
    if request.method == 'POST':
        article_id = request.form.get('article_id', type=int)
        quantity = request.form.get('quantity', type=float)
        unit_id = request.form.get('unit_id', type=int) # Unidad en la que se registra (Base o Compra)
        unit_cost = request.form.get('unit_cost', type=float) # Opcional: Actualizar costo
        observations = request.form.get('observations')
        
        if article_id and quantity and quantity > 0:
            article = Article.query.get(article_id)
            if article:
                # Lógica de Conversión Automática
                actual_quantity = quantity
                if unit_id == article.purchase_unit_id and article.conversion_factor:
                    actual_quantity = quantity * article.conversion_factor
                
                # Actualizar costo si se especificó (basado en unidad de registro)
                if unit_cost is not None and unit_cost > 0:
                    if unit_id == article.purchase_unit_id and article.conversion_factor:
                        # Si es unidad de compra, convertir costo a unidad base
                        article.unit_cost = unit_cost / article.conversion_factor
                    else:
                        article.unit_cost = unit_cost

                # Procesar Adjunto
                document_filename = None
                if 'document' in request.files:
                    file = request.files['document']
                    if file and file.filename != '':
                        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
                        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                        if ext in allowed_extensions:
                            # Generar nombre único: MOV_TIMESTAMP_RANDOM_filename
                            import time
                            import random
                            timestamp = int(time.time())
                            orig_name = secure_filename(file.filename)
                            document_filename = f"MOV_{timestamp}_{random.randint(1000,9999)}_{orig_name}"
                            file.save(os.path.join(current_app.config['MOVEMENTS_UPLOAD_FOLDER'], document_filename))
                        else:
                            flash('Formato de archivo no permitido. Use PDF, PNG o JPG.', 'warning')

                article.current_stock += actual_quantity
                movement = InventoryMovement(
                    movement_type='IN',
                    article_id=article_id,
                    quantity=actual_quantity,
                    movement_unit_id=unit_id,
                    user_id=current_user.id,
                    observations=observations,
                    document_filename=document_filename
                )
                db.session.add(movement)
                db.session.commit()
                
                # Mensaje dinámico de conversión
                msg = f'Se ingresaron {quantity} unidades locales de {article.name}.'
                if unit_id == article.purchase_unit_id:
                    msg = f'Ingreso: {quantity} {article.purchase_unit.name} -> {actual_quantity} {article.base_unit.name} totales.'
                
                flash(msg, 'success')
            return redirect(url_for('stock.inventory_in'))
            
    articles_list = Article.query.filter_by(status='Activo').all()
    categories_list = Category.query.all()
    units_list = Unit.query.all()
    return render_template('inventory_in.html', articles=articles_list, units=units_list, categories=categories_list)

@stock.route('/units/add', methods=['POST'])
@login_required
def add_unit():
    name = request.form.get('name', '').strip()
    abbr = request.form.get('abbreviation', '').strip()
    category = request.form.get('category') # Conteo, Masa, etc.
    description = request.form.get('description', '').strip()
    next_url = request.form.get('next', url_for('stock.articles'))
    
    if name and abbr and category:
        existing_name = Unit.query.filter(db.func.lower(Unit.name) == name.lower()).first()
        existing_abbr = Unit.query.filter(db.func.lower(Unit.abbreviation) == abbr.lower()).first()
        if existing_name:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Ya existe una unidad llamada "{existing_name.name}".'})
            flash(f'Ya existe una unidad llamada "{existing_name.name}".', 'danger')
        elif existing_abbr:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Ya existe una unidad con la abreviatura "{existing_abbr.abbreviation}".'})
            flash(f'Ya existe una unidad con la abreviatura "{existing_abbr.abbreviation}".', 'danger')
        else:
            new_unit = Unit(name=name, abbreviation=abbr, category=category, description=description)
            db.session.add(new_unit)
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': f'Unidad {abbr} creada exitosamente.'})
            flash(f'Unidad {abbr} creada exitosamente.', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Faltan datos para crear la unidad.'})
        flash('Faltan datos para crear la unidad.', 'danger')
    return redirect(next_url)

@stock.route('/inventory/out', methods=['GET', 'POST'])
@login_required
def inventory_out():
    if request.method == 'POST':
        article_id = request.form.get('article_id', type=int)
        quantity = request.form.get('quantity', type=float)
        department_id = request.form.get('department_id', type=int)
        receiver_name = request.form.get('receiver_name')
        receiver_cedula = request.form.get('receiver_cedula')
        observations = request.form.get('observations')
        
        if article_id and quantity and quantity > 0 and department_id:
            article = Article.query.get(article_id)
            if article:
                if article.current_stock >= quantity:
                    # Procesar Adjunto
                    document_filename = None
                    if 'document' in request.files:
                        file = request.files['document']
                        if file and file.filename != '':
                            allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
                            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                            if ext in allowed_extensions:
                                import time
                                import random
                                timestamp = int(time.time())
                                orig_name = secure_filename(file.filename)
                                document_filename = f"OUT_{timestamp}_{random.randint(1000,9999)}_{orig_name}"
                                file.save(os.path.join(current_app.config['MOVEMENTS_UPLOAD_FOLDER'], document_filename))

                    article.current_stock -= quantity
                    movement = InventoryMovement(
                        date=datetime.utcnow(),
                        movement_type='OUT',
                        article_id=article_id,
                        quantity=quantity,
                        movement_unit_id=article.base_unit_id, # Por defecto salidas en base_unit
                        user_id=current_user.id,
                        department_id=department_id,
                        receiver_name=receiver_name,
                        receiver_cedula=receiver_cedula,
                        observations=observations,
                        document_filename=document_filename
                    )
                    db.session.add(movement)
                    db.session.commit()

                    # SGI-NOTIFY: Trigger Telegram Alert if stock is too low
                    if article.current_stock <= article.min_stock:
                        config = InstitutionConfig.query.first()
                        if config and config.telegram_bot_token and config.telegram_chat_id:
                            try:
                                from app.utils import send_telegram_alert
                                send_telegram_alert(config.telegram_bot_token, config.telegram_chat_id, article)
                            except ImportError:
                                pass
                    
                    flash(f'Entrega registrada: {quantity} {article.base_unit.abbreviation} de {article.name}.', 'success')
                else:
                    flash(f'Stock insuficiente. Stock actual: {article.current_stock} {article.base_unit.abbreviation}', 'danger')
            return redirect(url_for('stock.inventory_out'))
            
    articles_list = Article.query.filter(Article.current_stock > 0).all()
    departments_list = Department.query.all()
    return render_template('inventory_out.html', articles=articles_list, departments=departments_list)

@stock.route('/inventory/adj', methods=['GET', 'POST'])
@login_required
def inventory_adj():
    if request.method == 'POST':
        article_id = request.form.get('article_id', type=int)
        new_quantity = request.form.get('new_quantity', type=float)
        observations = request.form.get('observations', '').strip()
        
        if article_id is not None and new_quantity is not None:
            article = Article.query.get_or_404(article_id)
            old_quantity = article.current_stock
            diff = new_quantity - old_quantity
            
            if diff != 0:
                # Procesar Adjunto
                document_filename = None
                if 'document' in request.files:
                    file = request.files['document']
                    if file and file.filename != '':
                        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
                        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                        if ext in allowed_extensions:
                            import time
                            import random
                            timestamp = int(time.time())
                            orig_name = secure_filename(file.filename)
                            document_filename = f"ADJ_{timestamp}_{random.randint(1000,9999)}_{orig_name}"
                            file.save(os.path.join(current_app.config['MOVEMENTS_UPLOAD_FOLDER'], document_filename))

                article.current_stock = new_quantity
                # Registrar el ajuste como un movimiento especial 'ADJ'
                movement = InventoryMovement(
                    movement_type='ADJ',
                    article_id=article_id,
                    quantity=diff, # La diferencia (positiva o negativa)
                    movement_unit_id=article.base_unit_id,
                    user_id=current_user.id,
                    observations=f"Ajuste Manual: De {old_quantity} a {new_quantity}. Motivo: {observations}",
                    document_filename=document_filename
                )
                db.session.add(movement)
                db.session.commit()
                flash(f'Ajuste realizado: {article.name} ahora tiene {new_quantity} {article.base_unit.abbreviation}.', 'success')
            else:
                flash('No se realizaron cambios (la cantidad es la misma).', 'info')
            return redirect(url_for('stock.inventory_adj'))

    articles_list = Article.query.all()
    return render_template('inventory_adj.html', articles=articles_list)

@stock.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('dashboard.index'))
    
    # Buscar en Artículos
    articles_results = Article.query.filter(
        db.or_(
            Article.name.ilike(f'%{query}%'),
            Article.observations.ilike(f'%{query}%'),
            Article.location.ilike(f'%{query}%')
        )
    ).all()
    
    # Buscar en Categorías
    categories_results = Category.query.filter(
        db.or_(
            Category.name.ilike(f'%{query}%'),
            Category.description.ilike(f'%{query}%')
        )
    ).all()
    
    # Buscar en Departamentos
    departments_results = Department.query.filter(
        db.or_(
            Department.name.ilike(f'%{query}%'),
            Department.description.ilike(f'%{query}%'),
            Department.manager_name.ilike(f'%{query}%')
        )
    ).all()
    
    return render_template('search.html', 
                           query=query, 
                           articles=articles_results, 
                           categories=categories_results, 
                           departments=departments_results)


@stock.route('/inventory/alerts')
@login_required
def alerts():
    # Artículos con stock bajo el mínimo
    critical_articles = Article.query.filter(Article.current_stock <= Article.min_stock, Article.status == 'Activo').all()
    
    # Alertas registradas pendientes
    pending_alerts = StockAlert.query.filter_by(status='Pendiente').order_by(StockAlert.alert_date.desc()).all()
    
    return render_template('stock_alerts.html', articles=critical_articles, alerts=pending_alerts)

@stock.route('/inventory/alerts/resolve/<int:id>', methods=['POST'])
@login_required
def resolve_alert(id):
    alert = StockAlert.query.get_or_404(id)
    alert.status = 'Resuelta'
    alert.resolved_date = datetime.utcnow()
    db.session.commit()
    flash('Alerta marcada como resuelta.', 'success')
    return redirect(url_for('stock.alerts'))
