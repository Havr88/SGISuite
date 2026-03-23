# Análisis de Compatibilidad Cloud y Despliegue

Este documento analiza la viabilidad de desplegar el **Sistema de Gestión de Inventario** en plataformas de nube y servicios VPS.

## 1. Análisis de Plataformas Nube (Serverless)

### Vercel / Cloudflare Pages
Ambas plataformas permiten desplegar aplicaciones Flask, pero presentan desafíos para este sistema específico:

- **Persistencia de Datos:** SQLite utiliza un archivo local. En Vercel y Cloudflare Pages, el sistema de archivos es temporal o efímero.
- **Solución Multi-DB:** El sistema ahora soporta conexión a bases de datos externas mediante la variable de entorno `DATABASE_URL`.
- **Configuración:** Para usar una base de datos persistente en la nube:
  1.  Cree una base de datos PostgreSQL o MySQL (ej. en Supabase, Railway, Neon).
  2.  Configure la variable `DATABASE_URL` con la cadena de conexión correspondiente.
  3.  El sistema detectará automáticamente el motor y usará la base de datos externa en lugar de SQLite.

## 2. Configuración de Base de Datos

El sistema utiliza `python-dotenv` para cargar configuraciones. Puede copiar el archivo de ejemplo y editarlo:

```bash
cp .env.example .env
nano .env
```

### Formatos de `DATABASE_URL` admitidos:
- **PostgreSQL:** `postgresql://usuario:password@host:5432/nombre_db`
- **MySQL:** `mysql+pymysql://usuario:password@host:3306/nombre_db`
- **SQLite (Por defecto):** Si no se define la variable, se usará `instance/inventory.sqlite`.

## 3. Análisis de Proveedores VPS (CubePath)

### CubePath
[CubePath](https://cubepath.com) es una solución de VPS y Nube Privada. Es la opción **altamente recomendada** para este proyecto debido a:

- **Infraestructura Tradicional:** Al ser un servidor virtual dedicado (VPS), ofrece un sistema de archivos persistente. SQLite funcionará sin problemas, guardando los datos permanentemente en el disco SSD/NVMe del servidor.
- **Debian 13:** CubePath permite instalar Debian 13 "Bookworm" de forma nativa.
- **Configuración de Red Local:** Ofrecen opciones de red privada que coinciden con los flujos offline/intranet planteados en el diseño original.

## 3. Estrategia de Despliegue en CubePath (Recomendada)

1.  **Aprovisionamiento:** Inicie una instancia de Cloud VPS con Debian 13.
2.  **Preparación:** Siga la [Guía de Instalación](INSTALL.md).
3.  **Seguridad:** Habilite el firewall `ufw` permitiendo solo los puertos 80, 443 (Nginx) y 22 (SSH).
4.  **Certificado SSL:** Si accede vía dominio, use Certbot. Si es puramente Intranet, use los certificados autofirmados generados durante la instalación de Nginx.

## 4. Matriz de Resumen

| Plataforma | Compatibilidad | Notas Técnicas |
| :--- | :--- | :--- |
| **CubePath** | ⭐⭐⭐⭐⭐ | **Excelente.** Soporte nativo para SQLite y persistencia total. |
| **Vercel** | ⭐⭐ | Posible, pero requiere DB externa (Postgres/MySQL) para ser funcional. |
| **Cloudflare** | ⭐⭐ | Igual que Vercel. Excelente para el frontend, pero la DB local es inviable. |

---

**Copyright (C) 2026 Henry Villarroel.**
