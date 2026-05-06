# TusSalonesEventos - Backend API

Este proyecto es el backend para la gestión de salones y eventos, desarrollado con Laravel 13 y enfocado exclusivamente en servicios API.

## Requisitos
* Docker Desktop
* Composer (para instalaciones locales)

## Configuración del Entorno (Docker + Sail)

Este proyecto utiliza **Laravel Sail** para gestionar el entorno de desarrollo. La base de datos configurada es **PostgreSQL**.

### 1. Iniciar los contenedores
Para levantar los servicios (PHP, PostgreSQL, Redis, etc.), ejecuta:
```bash
./vendor/bin/sail up -d
```

### 2. Ejecutar Migraciones
Una vez que los contenedores estén corriendo, prepara la base de datos:
```bash
./vendor/bin/sail artisan migrate
```

### 3. Acceso a la API
La API estará disponible en `http://localhost`.

---

## Desarrollo y Tareas
El desarrollo está dividido en módulos independientes:
* **Módulo de Eventos**: Gestionado en la rama `JavierRodriguez-Develop`.
* **Módulo de Salones/Tickets**: Gestionado en la rama `CesarJankarlo-Develop`.

### Reglas de Desarrollo
* **Solo vía API**: Todo el intercambio de datos debe realizarse a través de endpoints JSON.
* **Autenticación**: Los servicios deben consumir y validar `userauth_id` y `app_id`.
* **Base de Datos**: Utilizar PostgreSQL (configurado automáticamente en Docker).

---

## Comandos Útiles de Sail
* Levantar servicios: `./vendor/bin/sail up -d`
* Detener servicios: `./vendor/bin/sail stop`
* Ejecutar artisan: `./vendor/bin/sail artisan [comando]`
* Ejecutar composer: `./vendor/bin/sail composer [comando]`
* Ejecutar tests: `./vendor/bin/sail test`
