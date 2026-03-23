from flask import Blueprint, render_template, request, make_response
from flask_login import login_required, current_user
from app.models import db, InventoryMovement, InstitutionConfig
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

reports = Blueprint('reports', __name__)

@reports.route('/reports/movements')
@login_required
def movements():
    from datetime import datetime
    from sqlalchemy import extract
    from app.models import Article, Department
    
    # Obtener filtros de la URL
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    article_id = request.args.get('article_id', type=int)
    department_id = request.args.get('department_id', type=int)
    
    query = InventoryMovement.query
    
    if year:
        query = query.filter(extract('year', InventoryMovement.date) == year)
    if month:
        query = query.filter(extract('month', InventoryMovement.date) == month)
    if article_id:
        query = query.filter(InventoryMovement.article_id == article_id)
    if department_id:
        query = query.filter(InventoryMovement.department_id == department_id)
    
    movements = query.order_by(InventoryMovement.date.desc()).all()
    articles = Article.query.all()
    departments = Department.query.all()
    
    return render_template('report_movements.html', 
                           movements=movements,
                           articles=articles,
                           departments=departments,
                           current_month=month,
                           current_year=year,
                           current_article_id=article_id,
                           current_department_id=department_id)

def _get_movement_data_and_config(month=None, year=None, article_id=None, department_id=None):
    from sqlalchemy import extract
    query = InventoryMovement.query
    if year:
        query = query.filter(extract('year', InventoryMovement.date) == year)
    if month:
        query = query.filter(extract('month', InventoryMovement.date) == month)
    if article_id:
        query = query.filter(InventoryMovement.article_id == article_id)
    if department_id:
        query = query.filter(InventoryMovement.department_id == department_id)
        
    movements_data = query.order_by(InventoryMovement.date.desc()).all()
    config = InstitutionConfig.query.first()
    return movements_data, config

@reports.route('/reports/movements/pdf')
@login_required
def download_movements_pdf():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    article_id = request.args.get('article_id', type=int)
    department_id = request.args.get('department_id', type=int)
    
    movements_data, config = _get_movement_data_and_config(month, year, article_id, department_id)
    inst_name = config.name if config else "Institución"
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    # Header
    elements.append(Paragraph(f"<b>{inst_name}</b>", title_style))
    elements.append(Paragraph("Reporte de Movimientos de Inventario (SGI-Docs+)", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Table Data
    data = [["Fecha", "Tipo", "Artículo", "Cantidad", "Usuario/Destino"]]
    for m in movements_data:
        date_str = m.date.strftime('%d/%m/%Y %H:%M')
        m_type = "INGRESO" if m.movement_type == 'IN' else "ENTREGA"
        art_name = m.article.name if m.article else 'N/A'
        
        # Uso de unidades técnicas
        qty = f"{m.quantity} {m.article.unit if m.article else ''}"
        
        # Lógica de destino detallada para egresos
        if m.movement_type == 'OUT':
            dest_parts = []
            if m.department: dest_parts.append(m.department.name)
            if m.receiver_name: dest_parts.append(f"Recibe: {m.receiver_name}")
            if m.receiver_cedula: dest_parts.append(f"ID: {m.receiver_cedula}")
            dest = "\n".join(dest_parts) if dest_parts else "N/A"
        else:
            dest = f"Carga: {m.user.username}" if m.user else "Sistema"
            
        data.append([date_str, m_type, art_name, qty, dest])
        
    # Table Style
    t = Table(data, colWidths=[100, 70, 150, 70, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    pdf_out = buffer.getvalue()
    buffer.close()
    
    response = make_response(pdf_out)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_movimientos.pdf'
    return response

@reports.route('/reports/correlation')
@login_required
def correlation():
    from datetime import datetime
    import calendar
    from app.models import Article
    
    month = request.args.get('month', type=int, default=datetime.now().month)
    year = request.args.get('year', type=int, default=datetime.now().year)
    
    # Fecha de inicio y fin del mes seleccionado
    last_day = calendar.monthrange(year, month)[1]
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day, 23, 59, 59)
    
    articles = Article.query.all()
    correlation_data = []
    
    for art in articles:
        # Stock al final del mes = Stock Actual - Net(movimientos después de end_date)
        net_after = db.session.query(
            db.func.sum(db.case((InventoryMovement.movement_type == 'IN', InventoryMovement.quantity), else_=-InventoryMovement.quantity))
        ).filter(InventoryMovement.article_id == art.id, InventoryMovement.date > end_date).scalar() or 0
        
        closing_stock = art.current_stock - net_after
        
        # Movimientos durante el mes
        ins_month = db.session.query(db.func.sum(InventoryMovement.quantity)).filter(
            InventoryMovement.article_id == art.id,
            InventoryMovement.movement_type == 'IN',
            InventoryMovement.date >= start_date,
            InventoryMovement.date <= end_date
        ).scalar() or 0
        
        outs_month = db.session.query(db.func.sum(InventoryMovement.quantity)).filter(
            InventoryMovement.article_id == art.id,
            InventoryMovement.movement_type == 'OUT',
            InventoryMovement.date >= start_date,
            InventoryMovement.date <= end_date
        ).scalar() or 0
        
        opening_stock = closing_stock - ins_month + outs_month
        
        correlation_data.append({
            'article': art,
            'opening': opening_stock,
            'ins': ins_month,
            'outs': outs_month,
            'closing': closing_stock
        })
        
    return render_template('inventory_correlation.html',
                           data=correlation_data,
                           current_month=month,
                           current_year=year)
