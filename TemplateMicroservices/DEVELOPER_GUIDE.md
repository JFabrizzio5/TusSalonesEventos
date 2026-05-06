# 📖 Guía del Desarrollador: Creando Tablas y Esquemas

Esta guía explica cómo extender un microservicio generado por la **CometaX Microservices Framework** añadiendo nuevos módulos y tablas en la base de datos de forma profesional.

## 🚀 Global CLI: CometaX Essentials
La forma más rápida de interactuar con el ecosistema es mediante el comando global `cometax`.

### Instalación
Para activar el comando en todo tu sistema:
1.  Ve a la raíz del repositorio.
2.  Ejecuta `./setup_cometax.sh`.
3.  Sigue las instrucciones para mover el wrapper a `/usr/local/bin` o añadir el alias.

### Uso
Desde cualquier terminal, simplemente escribe:
```bash
cometax
```
Esto abrirá el **SaaS Factory Launcher** de forma instantánea.

---

## 1. Crear un Nuevo Módulo
Para mantener la arquitectura limpia, cada funcionalidad debe vivir en su propio "Módulo".

1.  Entra en la carpeta de tu microservicio.
2.  Ejecuta `./run.sh`.
3.  Selecciona **`📦 Módulos`** -> **`✨ Crear Nuevo Módulo`**.
4.  Asigna un nombre (Ej: `Pedidos`).

Esto creará la estructura: `modules/pedidos/models/models.py`, `services/`, `api/`, etc.

---

## 2. Definir tu Modelo (Tabla SQL)
Abre el archivo `modules/pedidos/models/models.py`. Verás que ya importa la `Base` centralizada.

```python
from sqlalchemy import Column, Integer, String, Boolean
from config.database import Base  # <--- IMPORTANTE

class Pedido(Base):
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(100), nullable=False)
    monto = Column(Integer, default=0)
    entregado = Column(Boolean, default=False)
```

> [!TIP]
> **No necesitas registrar este modelo en ningún otro lado.** El sistema de migraciones lo detectará automáticamente gracias al cargador dinámico en `migrations/env.py`.

---

## 3. Generar y Aplicar la Migración
Una vez definido el modelo, debes crear la tabla física en la base de datos (PostgreSQL).

1.  En el panel `./run.sh`, ve a **`🔄 Migraciones`**.
2.  Selecciona **`Crear`**.
3.  Escribe un mensaje descriptivo (Ej: `add pedidos table`).
    - *Esto generará un archivo en `migrations/versions/XXXX_add_pedidos_table.py`.*
4.  Selecciona **`Upgrade`**.
    - *Esto ejecutará el cambio en el contenedor de la base de datos.*

---

## 4. Verificar el Esquema
Puedes verificar que la tabla existe simplemente arrancando el microservicio (`🚀 Docker Up`). Si el microservicio inicia sin errores y puedes ver el log `ALEMBIC [alembic.runtime.migration] Context impl PostgresqlImpl...`, significa que tu esquema está sincronizado.

---

## 6. Orquestación y Resiliencia (Fase 2 & 3)
La comunicación entre microservicios en CometaX se realiza mediante el `InternalServiceClient`.

### Uso Básico
Puedes obtener un cliente para cualquier servicio del ecosistema:

```python
from core.internal_client import get_service_client

async def mi_funcion():
    # El nombre coincide con la variable de entorno API_PAYMENTS_URL
    payments = get_service_client("PAYMENTS")
    
    response = await payments.get("/v1/status")
    return response.json()
```

### Propagación de Identidad y Rastro
El cliente maneja automáticamente:
- **X-Request-ID**: Se propaga el ID de rastro original para debuggear flujos complejos.
- **Sentry Tracing**: Se propagan los headers de performance automáticamente.
- **Identidad**: Si tienes un token de usuario, pásalo para mantener sus permisos en el servicio destino:
  `await payments.get("/me", user_token=user['token'])`

### Resiliencia Automática
El cliente incluye reintentos automáticos con **Exponential Backoff**:
- Si una llamada falla por red o tiempo de espera, el sistema reintentará hasta **3 veces** antes de lanzar un error.
- Esto evita que fallos momentáneos de red causen errores al usuario final.

### Generar Wrappers (DDR: Don't Repeat Yourself)
Usa el CLI para generar clientes tipados rápidamente:
`./run.sh` -> Módulos -> Service Wrapper -> Escribir `payments`.
Esto creará `services/payments_client.py` con una estructura lista para extender.

---

## 7. Observabilidad y Monitoreo Enterprise (Sentry)
CometaX utiliza **Sentry** no solo para errores, sino para **Trazabilidad Distribuida**. Esto permite ver el viaje completo de una petición a través de múltiples microservicios.

### Cómo Encontrar un Rastro
1.  Entra en tu dashboard de **Sentry**.
2.  Ve a la pestaña **Performance** o **Discover**.
3.  Usa los filtros en la barra de búsqueda:
    - `transaction:NOMBRE_DE_TU_TRANSACCION` (Ej: `JOSEPH-SaaS-Enterprise-Flow`)
    - `environment:debug-joseph` (Para ver solo tus pruebas locales)

### Cómo Leer el Rastro (Trace View)
Cuando abras un evento, verás una **Jerarquía de Cascadas**:
- **Barra Principal (Morada)**: Representa el tiempo total desde que el usuario inició la petición.
- **Barra de Cliente (Salmón/Hijo)**: Es el momento exacto en que un servicio llamó a otro vía HTTP.
- **Barra de Servidor (Roja/Nieto)**: Es el momento en que el segundo microservicio recibió y procesó la petición.

> [!TIP]
> **Personalizar Nombres**: Sentry nombra las transacciones automáticamente por la ruta (e.g. `GET /v1/pedidos`), pero puedes sobrescribirlo con `sentry_sdk.set_transaction("Nombre-Personalizado")` al inicio de cualquier función para que aparezca con ese nombre exacto en el rastro.

### Casos de Uso: Workers y Cadenas de Llamadas
Para tareas en segundo plano (Arq Workers), es recomendable agrupar la lógica manualmente para mayor claridad:

```python
import sentry_sdk
from core.internal_client import get_service_client

async def mi_tarea_pesada(ctx, data: dict):
    # Agrupamos todo el trabajo del worker en una transacción única
    with sentry_sdk.start_transaction(name="WORKER: Procesamiento-Mensual"):
        # Si llamas a otro servicio aquí, el rastro continuará en el destino
        client = get_service_client("FACTURACION")
        await client.post("/generar", json=data)
```

### Debugging Local
Si quieres ver los IDs de rastro en tiempo real, revisa los logs de tu consola:
`🆔 Rastro (Sentry-Trace): [ID_LARGO]-[ID_SPAN]-1`
Este ID es el **"Pasaporte"** de tu petición. Puedes pegarlo en el buscador global de Sentry para encontrar todo lo relacionado con esa llamada específica.

---
*Escalabilidad y orden al estilo CometaX.*
