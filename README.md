# SGI Suite &bull; Sistema de Gestión de Inventario v1.0
> **Lanzamiento Oficial:** Sábado, 22 de Marzo de 2026

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![License: LVSL](https://img.shields.io/badge/License-LVSL-green.svg)](LICENSE_LVSL.md)
[![SGI Suite](https://img.shields.io/badge/Suite-SGI-orange.svg)](docs/SGI_VISION.md)

Este repositorio es el núcleo operativo de la **SGI Suite**, un ecosistema de software libre diseñado para la gestión de inventarios con enfoque en soberanía tecnológica y eficiencia operativa.

## 🚀 Características Principales

- **100% Offline:** Funciona en redes locales (Intranet) sin necesidad de internet.
- **Gestión Multi-institucional:** Configura los datos de tu institución y logo desde el panel administrativo.
- **Control de Stock:** Alertas automáticas para artículos con stock bajo o agotado.
- **Trazabilidad Total:** Registro detallado de quién entrega, quién recibe y a qué departamento va cada artículo.
- **Reportes Imprimibles:** Historial de movimientos listo para auditoría y reportes físicos.
- **Arquitectura Ligera:** Basado en Flask con soporte dinámico para SQLite, MariaDB y PostgreSQL.

---

### 🏆 Hackatón CubePath 2026
Este proyecto ha sido desarrollado y optimizado para la **Hackatón CubePath 2026**.

- **🌐 Demo en Vivo:** [SGI Suite en CubePath](https://hackaton2026.havr.cc/) 
- **☁️ Despliegue en CubePath:** Se ha utilizado la infraestructura de **CubePath** para el despliegue productivo, aprovechando su gestión de variables de entorno para la configuración dinámica de motores de base de Datos (MariaDB/Postgres) y su alta disponibilidad para garantizar el acceso institucional.

#### 📸 Vista Previa

## 🛠️ Tecnologías

- **Backend:** Python 3.13 + Flask
- **Base de Datos:** SQLite (Soporte nativo offline)
- **Frontend:** Jinja2 + CSS Vanilla (Sleek & Modern Design)
- **Servidor Recomendado:** Debian 13 (Bookworm) + Nginx + Gunicorn

## 📋 Requisitos Previos

- Python 3.13 o superior.
- Pip (Gestor de paquetes de Python).
- (Opcional) Entorno virtual `venv`.

## ⚙️ Instalación Rápida

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Havr88/SGISuite.git
   cd SGISuite/
   ```

2. **Preparar el entorno virtual :**
# Instalar dependencias del sistema (Debian/Ubuntu)
   ```bash
sudo apt update && sudo apt install python3-venv -y
   ```

# Crear y activar el entorno virtual
   ```bash
python3 -m venv venv
source venv/bin/activate
   ```

# Actualizar pip e instalar dependencias del proyecto
   ```bash
pip install --upgrade pip
pip install -r requirements.txt
   ```

# Instalar dependencias de Python:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Ejecutar la aplicación:**
   ```bash
   python run.py
      ```
Accede a `http://localhost:5000` en tu navegador.

## 📖 Documentación

Para una guía detallada, consulta los siguientes documentos:

- 📦 [Instalación Detallada](docs/INSTALL.md)
- 🖥️ [Guía de Uso](docs/USAGE.md)
- ☁️ [Guía de Despliegue (Nube y VPS)](docs/DEPLOYMENT.md)
- 🤝 [Cómo Contribuir](CONTRIBUTING.md)

## ⚖️ Licencia

Este proyecto cuenta con un esquema de doble licenciamiento:
- **Licencia Primaria:** [GNU Affero General Public License v3 (AGPLv3)](LICENSE)
- **Licencia Secundaria:** [Licencia Venezolana de Software Libre (LVSL)](LICENSE_LVSL.md)

**Autor 2026 Henry Villarroel.**

---

Desarrollado con ❤️ para la Soberanía Tecnológica.
