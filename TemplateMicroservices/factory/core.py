import os

def create_core_rt(project_path):
    """Crea la capa core: WebSockets, PubSub, Redis Streams y Cache con soporte para Testeo."""
    core_path = os.path.join(project_path, "core")
    os.makedirs(core_path, exist_ok=True)
    open(os.path.join(core_path, "__init__.py"), "a").close()
    
    # 1. WebSocket Manager (Soporte Multi-Servidor vía Redis PubSub)
    with open(os.path.join(core_path, "websockets.py"), "w") as f:
        f.write("""import logging
import json
import asyncio
import os
import redis.asyncio as aioredis
from typing import List, Dict
from fastapi import WebSocket

logger = logging.getLogger("websockets")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.redis = None
        self.pubsub = None
        self.channel_name = "ws_global_broadcast"

    async def connect_redis(self):
        url = os.getenv("REDIS_PUBSUB_URL", "redis://redis:6379/1")
        self.redis = await aioredis.from_url(url, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(self.channel_name)
        asyncio.create_task(self._listen_to_redis())
        logger.info("🔌 [WS] Conectado a Redis Backplane para WebSockets")

    async def _listen_to_redis(self):
        \"\"\"Escucha mensajes de otros servidores y los envía a clientes locales.\"\"\"
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    await self._local_broadcast(data["payload"])
        except Exception as e:
            logger.error(f"❌ [WS] Error en Redis Backplane: {e}")

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)

    async def broadcast(self, message: str):
        \"\"\"Publica el mensaje a Redis para que llegue a TODOS los servidores.\"\"\"
        if self.redis:
            await self.redis.publish(self.channel_name, json.dumps({"payload": message}))
        else:
            await self._local_broadcast(message)

    async def _local_broadcast(self, message: str):
        \"\"\"Envía el mensaje solo a las conexiones de este servidor.\"\"\"
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()
""")

    # 2. Redis Streams (Alta Performance - Reemplaza PubSub para escalabilidad)
    with open(os.path.join(core_path, "streams.py"), "w") as f:
        f.write("""import json
import redis.asyncio as aioredis
import os
import logging
from datetime import datetime

logger = logging.getLogger("streams")

class StreamsManager:
    \"\"\"Redis Streams es 10x más eficiente que PubSub normal para eventos masivos.\"\"\"
    def __init__(self):
        self.redis = None

    async def connect(self):
        url = os.getenv("REDIS_PUBSUB_URL", "redis://redis:6379/1") # DB 1 para Streams
        self.redis = await aioredis.from_url(url, decode_responses=True)
        logger.info("🌊 [STREAMS] Redis Streams Conectado (Infraestructura de Alta Performance)")

    async def add_event(self, stream_name: str, data: dict):
        \"\"\"XADD: Agrega un evento al rastro de Streams.\"\"\"
        if self.redis:
            data["_timestamp"] = datetime.now().isoformat()
            await self.redis.xadd(stream_name, {"payload": json.dumps(data)})

    async def get_stats(self, stream_name: str):
        if self.redis:
            return await self.redis.xlen(stream_name)

    async def consume_events(self, stream_name: str, count: int = 10, block: int = 5000):
        \"\"\"XREAD: Lee eventos del stream (Bloqueante para eficiencia).\"\"\"
        if self.redis:
            # Lee eventos nuevos desde el inicio (0) o el final ($)
            return await self.redis.xread({stream_name: "0-0"}, count=count, block=block)

streams_manager = StreamsManager()
""")

    # 3. Traceability (Compartido entre API y Worker)
    with open(os.path.join(core_path, "trace.py"), "w") as f:
        f.write("""from contextvars import ContextVar
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="CORE")
""")

    # 4. Cache Manager (Eficiencia y Tutorial de uso)
    with open(os.path.join(core_path, "cache.py"), "w") as f:
        f.write("""import json
import redis.asyncio as aioredis
import os
import functools
import logging

logger = logging.getLogger("cache")

class CacheManager:
    \"\"\"🚀 Manejador de Cache Global - Implementa @cached()\"\"\"
    def __init__(self):
        self.redis = None

    async def connect(self):
        url = os.getenv("REDIS_CACHE_URL", "redis://redis:6379/0") # DB 0 para Cache
        self.redis = await aioredis.from_url(url, decode_responses=True)
        logger.info("⚡ [CACHE] Redis Cache Conectado (Optimización Activa)")

    async def get(self, key: str):
        if not self.redis: return None
        value = await self.redis.get(f"cache:{key}")
        return json.loads(value) if value else None

    async def set(self, key: str, value: any, ttl: int = 300):
        if self.redis:
            await self.redis.setex(f"cache:{key}", ttl, json.dumps(value))

    def cached(self, ttl: int = 300):
        \"\"\"Tutorial: @cached(ttl=60) sobre cualquier función asíncrona.\"\"\"
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                key = f"{func.__name__}:{args}:{kwargs}"
                cached_val = await self.get(key)
                if cached_val: return cached_val
                result = await func(*args, **kwargs)
                await self.set(key, result, ttl)
                return result
            return wrapper
        return decorator

cache_manager = CacheManager()
""")

    # 5. Monitor Manager (Específico para Arq y Salud del Worker)
    with open(os.path.join(core_path, "monitor.py"), "w") as f:
        f.write("""import os
import logging
import redis.asyncio as aioredis
from config.redis_config import get_redis_settings

logger = logging.getLogger("monitor")

class MonitorManager:
    \"\"\"🚀 Monitor de Colas - Inspección en tiempo real de Arq\"\"\"
    def __init__(self):
        self.redis = None
        self.queue_name = os.getenv("QUEUE_NAME", "arq:queue")

    async def connect(self):
        settings = get_redis_settings("queue")
        url = f"redis://:{settings.password}@{settings.host}:{settings.port}/{settings.database}" if settings.password else f"redis://{settings.host}:{settings.port}/{settings.database}"
        self.redis = await aioredis.from_url(url, decode_responses=False)
        logger.info(f"📊 [MONITOR] Conectado a {self.queue_name}")


    async def get_stats(self):
        \"\"\"Retorna estadísticas resumidas de la cola y trabajos completados.\"\"\"
        depth = await self.get_queue_depth()
        # Intentar obtener contadores de Redis
        success = 0
        failed = 0
        if self.redis:
            val_s = await self.redis.get(f"{self.queue_name}:success")
            val_f = await self.redis.get(f"{self.queue_name}:failed")
            success = int(val_s) if val_s else 0
            failed = int(val_f) if val_f else 0

        return {
            "queue": self.queue_name,
            "pending_jobs": depth,
            "jobs_completed": success,
            "jobs_failed": failed,
            "status": "healthy" if self.redis else "disconnected"
        }

    async def report_success(self):
        \"\"\"Incrementa el contador de éxitos en Redis.\"\"\"
        if self.redis:
            await self.redis.incr(f"{self.queue_name}:success")

    async def report_failure(self):
        \"\"\"Incrementa el contador de fallos en Redis.\"\"\"
        if self.redis:
            await self.redis.incr(f"{self.queue_name}:failed")

monitor_manager = MonitorManager()
""")

    # 6. HTTP Client con Propagación de Trazabilidad
    with open(os.path.join(core_path, "http_client.py"), "w") as f:
        f.write("""import httpx
from core.trace import request_id_ctx_var

class TracedAsyncClient(httpx.AsyncClient):
    \"\"\"
    Cliente HTTP que inyecta automáticamente el X-Request-ID en 
    todas las peticiones salientes para mantener la trazabilidad distribuida.
    \"\"\"
    async def request(self, method: str, url: httpx._types.URLTypes, **kwargs):
        headers = kwargs.get("headers", {})
        # Inyectar Correlation ID actual
        current_id = request_id_ctx_var.get()
        if current_id and current_id != "CORE":
            headers["X-Request-ID"] = current_id
        
        kwargs["headers"] = headers
        return await super().request(method, url, **kwargs)

# Instancia global reutilizable (usar en vez de httpx.AsyncClient directo)
http_client = TracedAsyncClient(timeout=30.0)
""")

    # 7. Rate Limiting (Redis-based)
    with open(os.path.join(core_path, "ratelimit.py"), "w") as f:
        f.write("""import time
import os
import logging
import redis.asyncio as aioredis
from fastapi import Request, HTTPException
from core.trace import request_id_ctx_var

logger = logging.getLogger("ratelimit")

class RateLimiter:
    \"\"\"
    🚀 Rate Limiter distribuido usando Redis.
    Soporta límites por Usuario (JWT) o por IP.
    \"\"\"
    def __init__(self):
        self.redis = None

    async def connect(self):
        url = os.getenv("REDIS_CACHE_URL", "redis://redis:6379/0")
        self.redis = await aioredis.from_url(url, decode_responses=True)

    async def check(self, request: Request, limit: int = 60, window: int = 60):
        \"\"\"
        Verifica si la petición excede el límite.
        limit: Número de peticiones permitidas.
        window: Ventana de tiempo en segundos.
        \"\"\"
        if not self.redis:
            await self.connect()

        # Identificar al usuario (vía IAMMiddleware si existe) o IP
        user_id = getattr(request.state, "user_id", request.client.host)
        key = f"ratelimit:{user_id}:{request.url.path}"

        try:
            current = await self.redis.get(key)
            if current and int(current) >= limit:
                rid = request_id_ctx_var.get()
                logger.warning(f"⚠️ [{rid}] Rate limit excedido para {user_id} en {request.url.path}")
                raise HTTPException(status_code=429, detail="Too many requests. Try again later.")

            # Incrementar y establecer expiración si es nuevo
            async with self.redis.pipeline(transaction=True) as pipe:
                await pipe.incr(key)
                await pipe.expire(key, window)
                await pipe.execute()
            return True
        except Exception as e:
            if isinstance(e, HTTPException): raise e
            logger.error(f"❌ Error en RateLimiter: {e}")
            return True # Fall-safe: Permitir si Redis falla

limiter = RateLimiter()
""")

    # 8. Auth & Security (RS256 Distributed Auth)
    with open(os.path.join(core_path, "security.py"), "w") as f:
        f.write("""import os
import jwt
from typing import Optional, Dict
from fastapi import HTTPException, status
import logging

logger = logging.getLogger("security")

# RS256: Solo usamos la LLAVE PÚBLICA para validar (Seguridad Asimétrica)
AUTH_PUBLIC_KEY = os.getenv("AUTH_PUBLIC_KEY", "")
ALGORITHM = "RS256"

def decode_access_token(token: str) -> Optional[Dict]:
    \"\"\"Valida un token JWT con la llave pública de ApiIam.\"\"\"
    try:
        if not AUTH_PUBLIC_KEY:
            logger.error("❌ [SECURITY] AUTH_PUBLIC_KEY no configurada")
            return None
        
        # El token puede venir con saltos de línea o formato PEM, lo manejamos
        public_key = AUTH_PUBLIC_KEY.replace("\\\\n", "\\n")
        
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("⚠️ [SECURITY] Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"❌ [SECURITY] Token inválido: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ [SECURITY] Error inesperado validando token: {e}")
        return None
""")

    with open(os.path.join(core_path, "auth.py"), "w") as f:
        f.write("""from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .security import decode_access_token

# El tokenUrl es referencial para Swagger, el login real vive en ApiIam
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    \"\"\"Dependencia para obtener el usuario actual validando el JWT.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación faltante",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraemos información común del payload de ApiIam
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene identificación de usuario",
        )
        
    return {
        "id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role"),
        "tenant_id": payload.get("tenant_id"),
        "payload": payload
    }

def requires_role(role: str):
    \"\"\"Dependencia para restringir rutas por rol.\"\"\"
    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere el rol de {role}",
            )
        return user
    return role_checker
""")

    # 9. Internal Service Client (Orquestación + Resiliencia)
    with open(os.path.join(core_path, "internal_client.py"), "w") as f:
        f.write('''import os
import httpx
import logging
import sentry_sdk
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from core.trace import request_id_ctx_var

logger = logging.getLogger("internal_client")

class InternalServiceClient:
    """
    🚀 Cliente principal para comunicación entre microservicios.
    Maneja automáticamente Auth Forwarding, Trazabilidad y RESILIENCIA.
    """
    def __init__(self, service_name: str, base_url: Optional[str] = None):
        self.service_name = service_name.upper()
        # Descubrimiento: Prioriza base_url manual, luego variable de entorno
        self.base_url = base_url or os.getenv(f"API_{self.service_name}_URL")
        self.timeout = httpx.Timeout(30.0, connect=5.0)
        
        if not self.base_url:
            logger.warning(f"⚠️ [INTERNAL] URL para servicio {self.service_name} no configurada (API_{self.service_name}_URL)")

    def _get_headers(self, user_token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "X-Request-ID": request_id_ctx_var.get() or "INTERNAL",
            "Content-Type": "application/json"
        }
        
        # 1. Forwarding: Si recibimos un token de usuario, lo propagamos
        if user_token:
            headers["Authorization"] = f"Bearer {user_token}"
        # 2. M2M: Si no hay usuario, usamos la App Key interna para Auth de sistema
        else:
            internal_key = os.getenv("INTERNAL_APP_KEY")
            if internal_key:
                headers["X-Internal-Key"] = internal_key
        
        # 3. Sentry Tracing: Propagación de rastro distribuido
        with sentry_sdk.configure_scope() as scope:
            # Sentry inyecta automáticamente 'sentry-trace' y 'baggage' si hay un hub activo
            # pero aquí nos aseguramos de que el cliente HTTP los soporte
            pass 
                
        return headers

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError, httpx.HTTPStatusError)),
        reraise=True
    )
    async def request(
        self, 
        method: str, 
        endpoint: str, 
        user_token: Optional[str] = None, 
        **kwargs
    ) -> httpx.Response:
        """
        Ejecuta una petición asíncrona con reintentos automáticos (Phase 3).
        Propaga el contexto de Sentry para trazabilidad distribuida (Phase 4).
        """
        if not self.base_url:
            raise Exception(f"URL de servicio {self.service_name} no definida")

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers(user_token)
        
        # Combinar headers adicionales si existen
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Sentry: Propagación de cabeceras de trazabilidad
        sentry_headers = sentry_sdk.get_traceparent()
        if sentry_headers:
            headers["sentry-trace"] = sentry_headers
        
        baggage = sentry_sdk.get_baggage()
        if baggage:
            headers["baggage"] = baggage

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, headers=headers, **kwargs)
                # Solo reintentamos errores de servidor 5xx si el usuario lo desea,
                # pero por defecto raise_for_status() lanzará la excepción.
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                # Si es 5xx, reintentamos (aquí podrías filtrar si quieres reintentar 500s)
                if e.response.status_code >= 500:
                    logger.warning(f"⚠️ [INTERNAL] Reintentando por error {e.response.status_code} en {self.service_name}...")
                    raise e # Tenacity lo capturará si configuramos retry_if_result
                logger.error(f"❌ [INTERNAL] Error {e.response.status_code} llamando a {self.service_name}: {e.response.text}")
                raise e
            except Exception as e:
                logger.error(f"❌ [INTERNAL] Error de conexión con {self.service_name}: {e}")
                raise e

    async def get(self, endpoint: str, **kwargs): return await self.request("GET", endpoint, **kwargs)
    async def post(self, endpoint: str, **kwargs): return await self.request("POST", endpoint, **kwargs)
    async def put(self, endpoint: str, **kwargs): return await self.request("PUT", endpoint, **kwargs)
    async def delete(self, endpoint: str, **kwargs): return await self.request("DELETE", endpoint, **kwargs)

# Factory para crear clientes de forma sencilla
def get_service_client(service_name: str) -> InternalServiceClient:
    return InternalServiceClient(service_name)
''')
