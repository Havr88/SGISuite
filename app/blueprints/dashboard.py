from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Article, Category, InventoryMovement, db
from app import cache  # Import the cache extension
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@dashboard.route('/dashboard')
@login_required
@cache.cached(timeout=60, key_prefix='sgi_dashboard_data')
def index():
    # Calculate stats for dashboard
    total_articles = Article.query.count()
    total_categories = Category.query.count()
    low_stock_articles = Article.query.filter(Article.current_stock <= Article.min_stock).count()
    
    # Get critical articles
    critical_articles = Article.query.filter(Article.current_stock <= Article.min_stock).all()
    
    # Recent movements
    recent_movements = InventoryMovement.query.order_by(InventoryMovement.date.desc()).limit(10).all()
    
    # --- CHART DATA CALCULATION ---
    # 1. Stock by Category (Pie Chart)
    categories_data = db.session.query(Category.name, func.count(Article.id))\
        .join(Article, Category.id == Article.category_id)\
        .group_by(Category.id).all()
    
    labels_pie = [c[0] for c in categories_data]
    data_pie = [c[1] for c in categories_data]
    
    # 2. Outgoings in the last 7 days (Bar Chart)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    outgoings = db.session.query(
        func.date(InventoryMovement.date).label('day'),
        func.sum(InventoryMovement.quantity).label('total')
    ).filter(InventoryMovement.movement_type == 'OUT', InventoryMovement.date >= seven_days_ago)\
     .group_by('day').order_by('day').all()
    
    labels_bar = [str(o[0]) for o in outgoings]
    data_bar = [int(o[1]) for o in outgoings]

    return render_template('dashboard.html', 
                           total_articles=total_articles,
                           total_categories=total_categories,
                           low_stock_articles=low_stock_articles,
                           critical_articles=critical_articles,
                           recent_movements=recent_movements,
                           labels_pie=labels_pie,
                           data_pie=data_pie,
                           labels_bar=labels_bar,
                           data_bar=data_bar,
                           view_mode='hub')

@dashboard.route('/analytics')
@login_required
@cache.cached(timeout=60, key_prefix='sgi_analytics_data')
def analytics():
    # Reuse same logic for analytics view
    total_articles = Article.query.count()
    total_categories = Category.query.count()
    low_stock_articles = Article.query.filter(Article.current_stock <= Article.min_stock).count()
    critical_articles = Article.query.filter(Article.current_stock <= Article.min_stock).all()
    recent_movements = InventoryMovement.query.order_by(InventoryMovement.date.desc()).limit(10).all()
    
    categories_data = db.session.query(Category.name, func.count(Article.id))\
        .join(Article, Category.id == Article.category_id)\
        .group_by(Category.id).all()
    labels_pie = [c[0] for c in categories_data]
    data_pie = [c[1] for c in categories_data]
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    outgoings = db.session.query(
        func.date(InventoryMovement.date).label('day'),
        func.sum(InventoryMovement.quantity).label('total')
    ).filter(InventoryMovement.movement_type == 'OUT', InventoryMovement.date >= seven_days_ago)\
     .group_by('day').order_by('day').all()
    
    labels_bar = [str(o[0]) for o in outgoings]
    data_bar = [int(o[1]) for o in outgoings]

    return render_template('dashboard.html', 
                           total_articles=total_articles,
                           total_categories=total_categories,
                           low_stock_articles=low_stock_articles,
                           critical_articles=critical_articles,
                           recent_movements=recent_movements,
                           labels_pie=labels_pie,
                           data_pie=data_pie,
                           labels_bar=labels_bar,
                           data_bar=data_bar,
                           view_mode='analytics')
