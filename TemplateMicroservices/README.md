# 🏭 CometaX Microservices Framework: Plantilla de Microservicios Core

Bienvenido a la versión **4.0** de nuestra plantilla de automatización para microservicios. Este framework ha sido diseñado meticulosamente para proporcionar infraestructuras altamente escalables, seguridad de acceso empresarial (IAM), descubrimiento dinámico de recursos, trazabilidad distribuida y ahora **capacidades avanzadas de Inteligencia Artificial (Vector Support)**.

---

## 🌟 Novedades en CometaX Microservices Framework

### 🔄 Puertos Dinámicos y Sincronización Remota
A diferencia de versiones anteriores con puertos estáticos, el **CometaX Microservices Framework** gestiona la infraestructura de forma inteligente:

-   **Bloque de 10 Puertos**: Cada microservicio obtiene un bloque de 10 puertos exclusivos asignados por el IAM (Control Plane).
    -   `API_PORT`: Base (ej: 8010)
    -   `POSTGRES_PORT`: Base + 1
    -   `PGBOUNCER_PORT`: Base + 2
    -   `REDIS_PORT`: Base + 3
    -   `MONGO_PORT`: Base + 4
    -   `PROMETHEUS_PORT`: Base + 5
    -   `GRAFANA_PORT`: Base + 6

-   **Cloud-First Config**: El microservicio intenta descargar su configuración desde el IAM al arrancar. Si no hay conexión o configuración remota, utiliza el modo **Fallback (Local .env)**.

-   **Docker Panel Sync**: Las imágenes y configuraciones de `docker-compose.yml` (como versiones de Postgres o Redis) se pueden gestionar centralizadamente desde el panel del IAM.

---

## 🚀 Guía de Inicio Rápido

### 1. Inicializar Nuevo Proyecto
Para generar la cascara de tu microservicio interactivo:
```bash
python3 launcher.py
```
Aparecerá un wizard para que definas el nombre y el tipo de persistencia (SQL, NoSQL, Ambos, Excel o Ninguno). El CLI generará un venv, compilará la infraestructura base y descargará los paquetes correspondientes.

### 2. Panel de Control Interactivo (`run.sh`)
Entra a la carpeta de tu nuevo microservicio generado y arranca el panel:
```bash
./run.sh
```
Desde aquí obtienes acceso a las siguientes herramientas:
- **Docker Up/Down**: Orquesta la cascara del microservicio y sus servicios de soporte local (Postgres/Mongo, Redis, PgBouncer).
- **Módulos (Module Wizard)**: Autogenera modelos, API routes, servicios y tareas asincrónicas. 

### 🔐 Registro Manual en IAM (Fallback)
Si al crear el microservicio el **Control Plane (ApiIam)** estaba offline, puedes registrarlo después en el panel del IAM usando el mismo nombre. El sistema es **idempotente** y actualizará los puertos una vez que el servicio sea capaz de contactar al servidor de configuración.

---
*Desarrollado con ❤️ y preparado para el futuro, equipo CometaX.*
