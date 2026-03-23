# Visión del Ecosistema SGI (Sistema de Gestión de Inventario)
**Autor:** Henry Villarroel (@Havr88)  
**Licencia:** GNU AGPLv3 + LVSL

## 🎯 Objetivo de la Suite
Convertir el sistema actual en una suite coherente de módulos interconectados que faciliten la soberanía tecnológica y la gestión eficiente de recursos.

## 🧱 Estructura Modular Propuesta

### 1. SGI-Auth (Módulo de Identidad)
- **Responsabilidad:** Seguridad, autenticación de usuarios, roles y permisos.
- **Estado Actual:** Integrado en el núcleo.
- **Evolución:** Soporte para LDAP/Active Directory y auditoría de sesiones.

### 2. SGI-Stock (Módulo de Operaciones)
- **Responsabilidad:** Gestión de artículos, categorías, ingresos y entregas.
- **Estado Actual:** Funcionalidad principal del sistema.
- **Evolución:** Soporte para escaneo de códigos de barra y QR.

### 3. SGI-Dash (Módulo de Inteligencia)
- **Responsabilidad:** Visualización de datos, estadísticas críticas y alertas de stock.
- **Estado Actual:** Dashboard básico de indicadores.
- **Evolución:** Gráficos dinámicos, proyecciones de consumo y exportación de KPIs.

### 4. SGI-Docs (Módulo de Reportes)
- **Responsabilidad:** Generación de guías de despacho, facturas y reportes PDF.
- **Estado Actual:** Reporte de movimientos imprimible.
- **Evolución:** Motor de PDFs avanzado y plantillas personalizables.

### 5. SGI-Libre (Repositorio Core)
- **Responsabilidad:** El motor base (Flask/SQLAlchemy) que permite la integración de todos los módulos anteriores.

## 🗺️ Roadmap de Evolución

### Fase 1: Branding y Modularización Lógica (Actual)
- Unificación bajo el prefijo **SGI**.
- Separación de rutas en Blueprints para facilitar el mantenimiento.
- Documentación técnica modular.

### Fase 2: Expansión de Funcionalidades
- **SGI-Venz:** Adaptaciones específicas para normativas legales venezolanas.
- **SGI-Sync:** API REST para sincronizar datos con agentes externos.

### Fase 3: Despliegue Avanzado
- Contenerización (Docker) para despliegues rápidos en CubePath.
- Soporte nativo para nubes serverless con bases de datos gestionadas.

---

> [!TIP]
> Esta visión permite que cada parte del sistema crezca de forma independiente, facilitando que otros contribuyentes se sumen al desarrollo de módulos específicos.
