from flask import Blueprint, jsonify, request
from app.models import Article, InstitutionConfig

api = Blueprint('api', __name__, url_prefix='/api/v1')

def check_api_key():
    config = InstitutionConfig.query.first()
    # If no api_key is configured, reject all requests
    if not config or not config.api_key:
        return False
        
    api_key = request.headers.get('X-API-Key')
    return api_key == config.api_key

@api.route('/stock', methods=['GET'])
def get_stock():
    if not check_api_key():
        return jsonify({"error": "Unauthorized. Invalid or missing X-API-Key."}), 401
        
    articles = Article.query.all()
    data = []
    for a in articles:
        data.append({
            "id": a.id,
            "name": a.name,
            "category": a.category.name if a.category else None,
            "current_stock": a.current_stock,
            "unit": a.unit,
            "min_stock": a.min_stock,
            "location": a.location,
            "status": "CRITICAL" if a.current_stock <= a.min_stock else "NORMAL"
        })
        
    return jsonify({
        "total_articles": len(data),
        "data": data
    }), 200

@api.route('/articles/<int:article_id>', methods=['GET'])
def get_article_details(article_id):
    if not check_api_key():
        return jsonify({"error": "Unauthorized. Invalid or missing X-API-Key."}), 401
        
    article = Article.query.get_or_404(article_id)
    return jsonify({
        "id": article.id,
        "name": article.name,
        "category": article.category.name if article.category else None,
        "current_stock": article.current_stock,
        "unit": article.unit,
        "min_stock": article.min_stock,
        "location": article.location,
        "observations": article.observations
    }), 200
