import os

def set_env_variable(key, value, env_file='.env'):
    """
    Actualiza o añade una variable en el archivo .env principal.
    """
    # Intentar leer el contenido actual
    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)
            
    if not found:
        # Añadir al final si no existe, asegurando nueva línea si el archivo no terminaba en una
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'
        new_lines.append(f"{key}={value}\n")
        
    # Escribir el nuevo contenido
    with open(env_file, 'w') as f:
        f.writelines(new_lines)

def get_db_config():
    """
    Retorna la configuración actual de BD desde el entorno.
    """
    return {
        'engine': os.environ.get('DB_ENGINE', 'sqlite'),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', ''),
        'user': os.environ.get('DB_USER', ''),
        'password': os.environ.get('DB_PASSWORD', ''),
        'name': os.environ.get('DB_NAME', 'inventory')
    }
