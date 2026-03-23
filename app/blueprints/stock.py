from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Category, Article, Department, InventoryMovement, InstitutionConfig
from datetime import datetime

stock = Blueprint('stock', __name__)

@stock.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if name:
            new_cat = Category(name=name, description=description)
            db.session.add(new_cat)
            db.session.commit()
            flash('Categoría agregada exitosamente.', 'success')
            
        next_url = request.form.get('next', url_for('stock.categories'))
        return redirect(next_url)
        
    cats = Category.query.all()
    return render_template('categories.html', categories=cats)

@stock.route('/departments', methods=['GET', 'POST'])
@login_required
def departments():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        manager_name = request.form.get('manager_name')
        manager_role = request.form.get('manager_role')
        manager_date_from = request.form.get('manager_date_from')
        manager_date_to = request.form.get('manager_date_to')
        
        d_from = None
        d_to = None
        if manager_date_from:
            d_from = datetime.strptime(manager_date_from, '%Y-%m-%d').date()
        if manager_date_to:
            d_to = datetime.strptime(manager_date_to, '%Y-%m-%d').date()

        if name:
            new_dep = Department(
                name=name, description=description,
                manager_name=manager_name, manager_role=manager_role,
                manager_date_from=d_from, manager_date_to=d_to
            )
            db.session.add(new_dep)
            db.session.commit()
            flash('Departamento agregado exitosamente.', 'success')
        
        next_url = request.form.get('next', url_for('stock.departments'))
        return redirect(next_url)
        
    deps = Department.query.all()
    return render_template('departments.html', departments=deps)

@stock.route('/categories/edit/<int:id>', methods=['POST'])
@login_required
def edit_category(id):
    cat = Category.query.get_or_404(id)
    cat.name = request.form.get('name')
    cat.description = request.form.get('description')
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
    dep.name = request.form.get('name')
    dep.description = request.form.get('description')
    dep.manager_name = request.form.get('manager_name')
    dep.manager_role = request.form.get('manager_role')
    
    m_from = request.form.get('manager_date_from')
    m_to = request.form.get('manager_date_to')
    # Use strftime format if matches, or handle appropriately
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
    from app.models import Unit
    articles_list = Article.query.all()
    categories_list = Category.query.all()
    units_list = Unit.query.all()
    return render_template('articles.html', articles=articles_list, categories=categories_list, units=units_list)

@stock.route('/articles/add', methods=['POST'])
@login_required
def add_article():
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    base_unit_id = request.form.get('base_unit_id', type=int)
    purchase_unit_id = request.form.get('purchase_unit_id', type=int)
    conversion_factor = request.form.get('conversion_factor', 1.0, type=float)
    location = request.form.get('location')
    min_stock = request.form.get('min_stock', 10.0, type=float)
    max_stock = request.form.get('max_stock', 100.0, type=float)
    observations = request.form.get('observations')
    
    if name and category_id and base_unit_id:
        article = Article(
            name=name, category_id=category_id, 
            base_unit_id=base_unit_id,
            purchase_unit_id=purchase_unit_id,
            conversion_factor=conversion_factor,
            location=location, min_stock=min_stock, max_stock=max_stock,
            current_stock=0.0, observations=observations
        )
        db.session.add(article)
        db.session.commit()
        flash('Artículo agregado exitosamente.', 'success')
    else:
        flash('Faltan datos obligatorios (Nombre, Categoría y Unidad Base).', 'danger')
        
    next_url = request.form.get('next', url_for('stock.articles'))
    return redirect(next_url)

@stock.route('/inventory/in', methods=['GET', 'POST'])
@login_required
def inventory_in():
    if request.method == 'POST':
        article_id = request.form.get('article_id', type=int)
        quantity = request.form.get('quantity', type=float)
        unit_id = request.form.get('unit_id', type=int) # Unidad en la que se registra (Base o Compra)
        observations = request.form.get('observations')
        
        if article_id and quantity and quantity > 0:
            article = Article.query.get(article_id)
            if article:
                # Lógica de Conversión Automática
                actual_quantity = quantity
                if unit_id == article.purchase_unit_id and article.conversion_factor:
                    actual_quantity = quantity * article.conversion_factor
                
                article.current_stock += actual_quantity
                movement = InventoryMovement(
                    movement_type='IN',
                    article_id=article_id,
                    quantity=actual_quantity,
                    movement_unit_id=unit_id,
                    user_id=current_user.id,
                    observations=observations
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
    from app.models import Unit
    units_list = Unit.query.all()
    return render_template('inventory_in.html', articles=articles_list, units=units_list, categories=categories_list)

@stock.route('/units/add', methods=['POST'])
@login_required
def add_unit():
    from app.models import Unit
    name = request.form.get('name')
    abbr = request.form.get('abbreviation')
    category = request.form.get('category') # Conteo, Masa, etc.
    description = request.form.get('description')
    
    if name and abbr and category:
        new_unit = Unit(name=name, abbreviation=abbr, category=category, description=description)
        db.session.add(new_unit)
        db.session.commit()
        flash(f'Unidad {abbr} creada exitosamente.', 'success')
    else:
        flash('Faltan datos para crear la unidad.', 'danger')
        
    next_url = request.form.get('next', url_for('stock.articles'))
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
                        observations=observations
                    )
                    db.session.add(movement)
                    db.session.commit()

                    # SGI-NOTIFY: Trigger Telegram Alert if stock is too low
                    if article.current_stock <= article.min_stock:
                        config = InstitutionConfig.query.first()
                        if config and config.telegram_bot_token and config.telegram_chat_id:
                            # Note: send_telegram_alert should be imported or defined
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
