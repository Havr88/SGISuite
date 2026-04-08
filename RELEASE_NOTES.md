# SGI Suite - Notas de Entrega v1.0.1

Esta versión marca la transición de un prototipo funcional a un sistema de gestión empresarial (ERP) ligero, robusto y preparado para auditorías técnicas y financieras avanzadas.

## 🌟 Resumen de Cambios Clave

Desde el lanzamiento inicial (v1.0), se han realizado las siguientes mejoras organizadas por dimensiones de impacto:

### 1. 💰 Dimensión Económico-Financiera (Valoración de Inventario)
- **Costo Unitario y Total**: Se incorporó el manejo de costos unitarios en cada entrada de mercancía.
- **Valorización en Tiempo Real**: El sistema ahora calcula automáticamente el valor total invertido en cada artículo y la inversión global del inventario, visible desde el Dashboard principal.
- **Trazabilidad en Reportes**: Se añadieron columnas de costo en los reportes de stock y movimientos para auditorías de presupuesto.

### 2. 📁 Dimensión Operativa y de Auditoría (Gestión Documental)
- **Soporte de Adjuntos Multi-Flujo**: Implementación completa de carga de archivos (PDF, PNG, JPG) para:
    - **Entradas**: Facturas de compra, actas de donación.
    - **Salidas**: Comprobantes de recepción firmados por departamentos.
    - **Ajustes**: Justificativos de auditoría o resolución de mermas.
- **Repositorio Seguro**: Configuración de almacenamiento persistente en el servidor con limpieza de nombres de archivo para seguridad.

### 3. 🧪 Estandarización de Datos (Framework CubePath)
- **Seeding Inteligente**: Se implementó una lógica de autocompletado de datos maestros al iniciar la aplicación.
- **Paquetes de Categorías**: Preconfiguración de categorías para Farmacia, Oficinas, Bodegas, Limpieza, Utilería y Mantenimiento.
- **Unidades de Medida Técnicas**: Integración de unidades estandarizadas (Unid., Blíster, Kg, Ml, Par, etc.) listas para su uso.

### 4. 📊 Reportes y Exportación
- **Exportación a Excel (XLSX)**: Se integró el soporte para generar reportes descargables en formato Excel, permitiendo el despliegue de datos fuera de la plataforma para análisis externo.
- **Búsqueda Global**: Optimización de la indexación de búsqueda para encontrar artículos, categorías y departamentos de forma simultánea.

### 5. 🎨 Interfaz y UX (Identidad Quantumm)
- **Estética Superior**: Aplicación de diseño **Glassmorphism** y una paleta de colores basada en **Violetas y Púrpuras**.
- **Tipografía Moderna**: Integración de la fuente **Quicksand** para mejorar la legibilidad académica y profesional.
- **Responsividad**: Ajustes en componentes modales y tablas para funcionamiento fluido en dispositivos móviles y tablets.

### 6. 🔐 Seguridad y Estabilidad
- **Protección CSRF**: Todas las transacciones de inventario ahora cuentan con protección contra ataques de falsificación de petición en sitios cruzados.
- **Gestión de Sesiones**: Reforzamiento del decorador `@login_required` en rutas sensibles.
- **Validación de Stock**: Implementación de bloqueos lógicos para evitar salidas de inventario superiores al stock actual disponible.

---

**SGI Suite v1.0.1** representa el compromiso con la **Soberanía Tecnológica** y la autogestión de recursos institucionales/empresariales.
