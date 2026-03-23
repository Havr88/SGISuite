# Guía de Instalación Detallada

Este documento explica cómo instalar el **Sistema de Gestión de Inventario** en un entorno local o de red privada, optimizado para **Debian 13**.

## 1. Preparación del Sistema

Asegúrate de tener instalado Python 13 y el gestor de paquetes pip.

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## 2. Configuración del Proyecto

### Clonación y Entorno Virtual

```bash
git clone https://github.com/tu-usuario/inventarios.git
cd inventarios/webapp

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate
```

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

## 3. Inicialización Automática

La aplicación está diseñada para autogestionar su base de datos. Al ejecutarla por primera vez:

1.  Crea la carpeta de instancia si no existe.
2.  Genera el archivo de base de datos SQLite predeterminado.
3.  Crea un usuario administrador por defecto:
    - **Usuario:** `admin`
    - **Contraseña:** `admin`

```bash
python run.py
```

## 4. Configuración para Producción (Nginx + Gunicorn)

Para un entorno multi-usuario en red local, se recomienda usar Gunicorn como servidor WSGI y Nginx como Proxy Inverso.

### Ejemplo de Archivo de Servicio (Systemd)

```ini
[Unit]
Description=Gunicorn instance to serve Inventory App
After=network.target

[Service]
User=tu-usuario
Group=www-data
WorkingDirectory=/ruta/a/inventarios/webapp
Environment="PATH=/ruta/a/inventarios/webapp/venv/bin"
ExecStart=/ruta/a/inventarios/webapp/venv/bin/gunicorn --workers 3 --bind unix:app.sock -m 007 run:app

[Install]
WantedBy=multi-user.target
```

---

**Copyright (C) 2026 Henry Villarroel.**
