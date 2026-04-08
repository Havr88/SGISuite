from app.models import db, Category, Unit

def seed_defaults():
    """Poblar la base de datos con categorías y unidades por defecto si no existen."""
    
    # 1. Unidades de Medida
    default_units = [
        {"name": "Unidad", "abbreviation": "und", "category": "Conteo"},
        {"name": "Caja", "abbreviation": "cja", "category": "Empaque"},
        {"name": "Paquete", "abbreviation": "pqt", "category": "Empaque"},
        {"name": "Litro", "abbreviation": "lt", "category": "Volumen"},
        {"name": "Galón", "abbreviation": "gl", "category": "Volumen"},
        {"name": "Kilogramo", "abbreviation": "kg", "category": "Masa"},
        {"name": "Gramo", "abbreviation": "gr", "category": "Masa"},
        {"name": "Metro", "abbreviation": "m", "category": "Longitud"},
        {"name": "Rollo", "abbreviation": "rl", "category": "Longitud"},
    ]
    
    for u_data in default_units:
        exists = Unit.query.filter_by(abbreviation=u_data["abbreviation"]).first()
        if not exists:
            unit = Unit(name=u_data["name"], abbreviation=u_data["abbreviation"], category=u_data["category"])
            db.session.add(unit)
            print(f"Semilla: Unidad '{u_data['name']}' añadida.")

    # 2. Categorías
    default_categories = [
        {
            "name": "Farmacia", 
            "description": "Medicamentos, insumos médicos, material descartable y quirúrgico."
        },
        {
            "name": "Oficina", 
            "description": "Suministros de papelería, consumibles de impresión y artículos de escritorio."
        },
        {
            "name": "Bodega / Almacén", 
            "description": "Insumos generales de almacenamiento, embalaje y logística interna."
        },
        {
            "name": "Limpieza", 
            "description": "Productos químicos de aseo, herramientas de limpieza y desinfección."
        },
        {
            "name": "Utilería", 
            "description": "Herramientas manuales, equipos eléctricos menores y accesorios de apoyo."
        },
        {
            "name": "Servicios Generales", 
            "description": "Materiales de plomería, electricidad, herrería y construcción ligera."
        },
        {
            "name": "Mantenimiento", 
            "description": "Repuestos, piezas críticas, lubricantes y suministros para conservación."
        }
    ]

    for c_data in default_categories:
        exists = Category.query.filter_by(name=c_data["name"]).first()
        if not exists:
            category = Category(name=c_data["name"], description=c_data["description"])
            db.session.add(category)
            print(f"Semilla: Categoría '{c_data['name']}' añadida.")
    
    try:
        db.session.commit()
        print("SGI-Seeds: Proceso de semillas completado con éxito.")
    except Exception as e:
        db.session.rollback()
        print(f"SGI-Seeds Error: {e}")
