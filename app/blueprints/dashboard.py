from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Article, Category, InventoryMovement, db
from app import cache  # Import the cache extension
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard = Blueprint('dashboard', __name__)

def _get_dashboard_data():
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

    # Valoración total (Fase 2)
    total_valuation = db.session.query(func.sum(Article.current_stock * Article.unit_cost)).scalar() or 0.0

    return {
        'total_articles': total_articles,
        'total_categories': total_categories,
        'low_stock_articles': low_stock_articles,
        'critical_articles': critical_articles,
        'recent_movements': recent_movements,
        'labels_pie': labels_pie,
        'data_pie': data_pie,
        'labels_bar': labels_bar,
        'data_bar': data_bar,
        'total_valuation': total_valuation
    }

@dashboard.route('/')
@dashboard.route('/dashboard')
@login_required
def index():
    data = _get_dashboard_data()
    return render_template('dashboard.html', view_mode='hub', **data)

@dashboard.route('/analytics')
@login_required
def analytics():
    data = _get_dashboard_data()
    return render_template('dashboard.html', view_mode='analytics', **data)
