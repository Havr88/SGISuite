import requests

def send_telegram_alert(bot_token, chat_id, article):
    """
    Envía una alerta de Telegram si el stock de un artículo es bajo.
    """
    if not bot_token or not chat_id:
        return False
        
    message = (
        f"🚨 *ALERTA SGI-NOTIFY* 🚨\n\n"
        f"El artículo *{article.name}* ha alcanzado su nivel crítico de stock.\n"
        f"🏷️ Categoría: {article.category.name}\n"
        f"📦 Stock Actual: {article.current_stock} {article.unit}\n"
        f"⚠️ Nivel Mínimo Riesgo: {article.min_stock} {article.unit}\n\n"
        f"📍 Ubicación: {article.location or 'No definida'}\n"
        f"💡 _Por favor, gestione la reposición lo antes posible._"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
