import os

def create_main_py(project_path, project_name, use_iam=True):
    """Genera main.py con Correlation ID, APP_NAME y logs trazables."""
    
    # ---------------- IAM BUNDLE ----------------
    iam_bundle = ""
    if use_iam:
        iam_bundle = """# --- MIDDLEWARE DE IAM Y TENANT (CON VALIDACIÓN REMOTA RS256) ---
import jwt
from core.cache import cache_manager

IAM_URL = os.getenv("IAM_URL", "http://localhost:8000")
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
EXPECTED_INTERNAL_APP_KEY = os.getenv("INTERNAL_APP_KEY")

def _is_public_path(path: str) -> bool:
    return path in ["/health", "/metrics", "/docs", "/openapi.json"]

async def get_public_key(kid: str):
    \"\"\"Obtiene la llave pública del IAM por su Key ID (kid) con caché en Redis.\"\"\"
    cache_key = f"jwk:{kid}"
    try:
        cached_jwk = await cache_manager.get(cache_key)
        if cached_jwk:
            from jwt import PyJWK
            return PyJWK(cached_jwk).key
        
        from core.http_client import http_client
        res = await http_client.get(f"{IAM_URL}/.well-known/jwks.json")
        if res.status_code == 200:
            jwks = res.json()
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    from jwt import PyJWK
                    await cache_manager.set(cache_key, key, ttl=300)
                    public_key = PyJWK(key).key
                    return public_key
    except Exception as e:
        logger.error(f"❌ Error obteniendo JWK del IAM: {e}")
    return None

class IAMMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if _is_public_path(request.url.path):
            return await call_next(request)

        internal_key = request.headers.get("X-Internal-Key")
        if internal_key:
            if not EXPECTED_INTERNAL_APP_KEY:
                logger.error("❌ INTERNAL_APP_KEY no configurado; no se permiten llamadas internas")
                return JSONResponse(status_code=503, content={"detail": "Servicio no configurado para llamadas internas"})
            if internal_key != EXPECTED_INTERNAL_APP_KEY:
                return JSONResponse(status_code=401, content={"detail": "Credencial interna inválida"})

            request.state.tenant_id = request.headers.get("X-Tenant-ID")
            request.state.user_id = "internal-service"
            request.state.is_internal = True
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                unverified_header = jwt.get_unverified_header(token)
                kid = unverified_header.get("kid")
                public_key = await get_public_key(kid)
                if not public_key:
                    return JSONResponse(status_code=401, content={"detail": "No se pudo obtener la llave pública de validación"})

                payload = jwt.decode(token, public_key, algorithms=["RS256"])
                tenant_id = payload.get("tenant_id")
                
                if tenant_id:
                    from core.http_client import http_client
                    try:
                        res = await http_client.get(f"{IAM_URL}/projects/v1/validate/{tenant_id}")
                        if res.status_code != 200:
                            return JSONResponse(status_code=403, content={"detail": "Proyecto/Tenant inactivo o no autorizado"})
                    except Exception as e:
                        logger.error(f"❌ Fallo al conectar con IAM para validar tenant: {e}")
                        return JSONResponse(status_code=503, content={"detail": "No se pudo validar tenant con IAM"})

                request.state.tenant_id = tenant_id
                request.state.user_id = payload.get("sub")
                request.state.is_internal = False
            except jwt.ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token expirado"})
            except Exception as e:
                logger.error(f"❌ Error de validación JWT: {e}")
                return JSONResponse(status_code=401, content={"detail": "Token inválido"})
        else:
            if REQUIRE_AUTH:
                return JSONResponse(status_code=401, content={"detail": "Autenticación requerida"})
            request.state.tenant_id = None
            request.state.user_id = None
            request.state.is_internal = False
            
        return await call_next(request)
"""
        
    # ---------------- BOOTSTRAP BUNDLE ----------------
    bootstrap_func = ""
    if use_iam:
        bootstrap_func = """async def bootstrap_remote_config():
    \"\"\"Consulta al IAM para cargar variables del .env remotas.\"\"\"
    key = os.getenv("IAM_PROJECT_KEY")
    if not key or "REPLACE_WITH_KEY" in key:
        logger.info("⚠️ [BOOTSTRAP] IAM_PROJECT_KEY no configurado. Usando variables locales.")
        return

    from core.http_client import http_client
    try:
        res = await http_client.get(f"{IAM_URL}/projects/v1/config", params={"key": key, "env": ENVIRONMENT})
        if res.status_code == 200:
            config = res.json()
            for k, v in config.items():
                os.environ[k] = str(v)
            logger.info(f"✅ [BOOTSTRAP] Configuración remota cargada desde IAM ({len(config)} variables)")
        else:
            logger.warning(f"⚠️ [BOOTSTRAP] IAM no devolvió config ({res.status_code}). Usando locales.")
    except Exception as e:
        logger.error(f"❌ [BOOTSTRAP] Error conectando con IAM: {e}")
"""

    iam_add_mid = "app.add_middleware(IAMMiddleware)" if use_iam else ""
    iam_lifespan_call = "    await bootstrap_remote_config()" if use_iam else "    pass # FASE 0: Sin IAM"

    main_content = f"""import os
import uuid
import asyncio
import logging
from contextlib import asynccontextmanager
from core.trace import request_id_ctx_var

# 1. CARGA TEMPRANA DE ENTORNO
from dotenv import load_dotenv
load_dotenv() # Carga el archivo .env maestro
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
load_dotenv(f".env.{{ENVIRONMENT}}", override=True) # Sobrescribe con el específico

import sentry_sdk
from sentry_sdk import metrics
from sentry_sdk.integrations.logging import LoggingIntegration
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from config.redis_config import get_redis_settings
from core.ratelimit import limiter

# --- CONFIGURACIÓN DE TRAZABILIDAD ---
APP_NAME = os.getenv("APP_NAME", "{project_name}")

class LogFilter(logging.Filter):
    def filter(self, record):
        record.app_name = APP_NAME
        record.request_id = request_id_ctx_var.get()
        return True

# Formato: [TIEMPO] [NIVEL] [APP_NAME] [ID_PETICION] Mensaje
format_str = "%(asctime)s - %(levelname)s - [%(app_name)s] [%(request_id)s] - %(message)s"
logging.basicConfig(level=logging.INFO, format=format_str)
for handler in logging.root.handlers:
    handler.addFilter(LogFilter())
logger = logging.getLogger("api_main")

# --- SENTRY SETUP ---
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")) # Leer del .env

if SENTRY_DSN:
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging],
        traces_sample_rate=SENTRY_SAMPLE_RATE, # Asignación dinámica
        enable_tracing=True,
        environment=ENVIRONMENT,
        release=f"{{APP_NAME.lower()}}@1.0.0",
        debug=False,
        enable_logs=True
    )
    sentry_sdk.set_tag("app_name", APP_NAME)
    logger.info(f"🚀 {{APP_NAME}} inicializado en {{ENVIRONMENT}} con Sentry Logs")
    sentry_sdk.capture_message(f"🚀 {{APP_NAME}} inicializado en {{ENVIRONMENT}}")

{iam_bundle}

# --- MIDDLEWARE DE REQUEST ID ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
        if ENVIRONMENT == "prod":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        token = request_id_ctx_var.set(rid)
        try:
            sentry_sdk.set_tag("request_id", rid)
            response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            request_id_ctx_var.reset(token)

from prometheus_client import Gauge, Counter
ARQ_QUEUE_DEPTH = Gauge("arq_queue_depth", "Jobs pending in Arq queue")
ARQ_SUCCESS_TOTAL = Counter("arq_success_total", "Total successful jobs")
ARQ_FAILED_TOTAL = Counter("arq_failed_total", "Total failed jobs")

async def arq_stats_poller():
    \"\"\"Actualiza las métricas de Prometheus cada 5 segundos.\"\"\"
    last_success = 0
    last_failed = 0
    while True:
        try:
            from core.monitor import monitor_manager
            stats = await monitor_manager.get_stats()
            ARQ_QUEUE_DEPTH.set(stats.get("pending_jobs", 0))
            diff_s = stats.get("jobs_completed", 0) - last_success
            if diff_s > 0:
                ARQ_SUCCESS_TOTAL.inc(diff_s)
                last_success = stats.get("jobs_completed", 0)
            diff_f = stats.get("jobs_failed", 0) - last_failed
            if diff_f > 0:
                ARQ_FAILED_TOTAL.inc(diff_f)
                last_failed = stats.get("jobs_failed", 0)
        except Exception:
            pass
        await asyncio.sleep(5)

{bootstrap_func}

# --- LIFESPAN (Infra Kickstart) ---
from core.cache import cache_manager
from core.streams import streams_manager
from core.monitor import monitor_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Iniciando {{APP_NAME}} en modo {{ENVIRONMENT}}")
    
    # FASE 0: Bootstrap Remoto
{iam_lifespan_call}

    for attempt in range(5):
        try:
            await cache_manager.connect()
            await streams_manager.connect()
            await monitor_manager.connect()
            await limiter.connect()
            from core.websockets import manager as ws_manager
            await ws_manager.connect_redis()
            asyncio.create_task(arq_stats_poller())
            logger.info("✅ [INFRA] Infraestructura Core Conectada exitosamente")
            break
        except Exception as e:
            logger.warning(f"⏳ [INFRA] Esperando a Redis/Infra (Intento {{attempt+1}}/5): {{e}}")
            await asyncio.sleep(2)
    else:
        logger.error("❌ [INFRA] Fallo crítico: La app arrancó en modo degradado (Sin Redis).")
    yield

app = FastAPI(title=f"{{APP_NAME}} API", lifespan=lifespan)
app.add_middleware(RequestIDMiddleware)
{iam_add_mid}
app.add_middleware(SecurityHeadersMiddleware)
cors_origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app)

@app.get("/queue/stats")
async def queue_stats():
    return await monitor_manager.get_stats()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    rid = request_id_ctx_var.get()
    logger.error(f"💥 [{{rid}}] Error no controlado: {{exc}}", exc_info=True)
    return JSONResponse(status_code=500, content={{"detail": "INTERNAL_SERVER_ERROR", "request_id": rid}})

@app.get("/health")
async def health():
    return {{"status": "ok", "app": APP_NAME, "id": request_id_ctx_var.get()}}

@app.get("/test-sentry")
async def test_sentry():
    logger.info("🧪 Generando rastro (breadcrumb) con el ID actual")
    logger.error("❌ Error de prueba para Sentry con ID de seguimiento")
    raise ValueError(f"Fallo detectado en {{APP_NAME}}")

@app.get("/test-metrics")
async def test_metrics():
    metrics.count("checkout.failed", 1, attributes={{"env": ENVIRONMENT}})
    metrics.gauge("queue.depth", 42, attributes={{"app": APP_NAME}})
    metrics.distribution("cart.amount_usd", 187.5, unit="dollar")
    return {{"status": "metrics_sent", "details": ["checkout.failed", "queue.depth", "cart.amount_usd"]}}

modules_path = os.path.join(os.path.dirname(__file__), "modules")
if os.path.exists(modules_path):
    import importlib
    for module_name in os.listdir(modules_path):
        mod_dir = os.path.join(modules_path, module_name)
        if os.path.isdir(mod_dir) and not module_name.startswith("__"):
            api_path = os.path.join(mod_dir, "api")
            if os.path.exists(api_path):
                for version in os.listdir(api_path):
                    v_dir = os.path.join(api_path, version)
                    if os.path.isdir(v_dir) and not version.startswith("__"):
                        try:
                            route_mod = importlib.import_module(f"modules.{{module_name}}.api.{{version}}.routes")
                            app.include_router(route_mod.router, prefix=f"/{{module_name.lower()}}/{{version}}", tags=[f"{{module_name.capitalize()}} {{version.upper()}}"])
                            try:
                                ws_mod = importlib.import_module(f"modules.{{module_name}}.api.{{version}}.websocket")
                                app.include_router(ws_mod.router)
                            except ImportError: pass
                        except Exception as e: logger.error(f"❌ Error cargando módulo {{module_name}} ({{version}}): {{e}}")
"""
    with open(os.path.join(project_path, "main.py"), "w") as f:
        f.write(main_content)

def create_worker_py(project_path, project_name):
    """Genera worker.py (Basado en Arq) para tareas en segundo plano."""
    worker_content = f"""import os
import asyncio
import logging
import importlib
from core.trace import request_id_ctx_var
from config.redis_config import get_redis_settings

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
APP_NAME = os.getenv("APP_NAME", "{project_name}")

class LogFilter(logging.Filter):
    def filter(self, record):
        record.app_name = APP_NAME
        record.request_id = request_id_ctx_var.get()
        return True

format_str = "%(asctime)s - %(levelname)s - [%(app_name)s] [%(request_id)s] - %(message)s"
logging.basicConfig(level=logging.INFO, format=format_str)
for handler in logging.root.handlers: handler.addFilter(LogFilter())
logger = logging.getLogger("worker")

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.INFO)
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[sentry_logging], traces_sample_rate=1.0, enable_tracing=True, environment=ENVIRONMENT, release=f"{{APP_NAME.lower()}}@1.0.0")
    sentry_sdk.set_tag("app_name", APP_NAME)
    logger.info(f"🚀 {{APP_NAME}} (Worker) listo en {{ENVIRONMENT}}")

async def health_check_task(ctx):
    logger.info("💓 [HEALTH] Worker pulse OK")
    return True

functions = [health_check_task]
modules_path = os.path.join(os.path.dirname(__file__), "modules")
if os.path.exists(modules_path):
    for module_name in os.listdir(modules_path):
        tasks_path = os.path.join(modules_path, module_name, "services", "tasks.py")
        if os.path.exists(tasks_path):
            try:
                module = importlib.import_module(f"modules.{{module_name}}.services.tasks")
                for name in dir(module):
                    attr = getattr(module, name)
                    if callable(attr) and not name.startswith("_"):
                        functions.append(attr)
                        logger.info(f"✅ [MODULE] {{module_name}} -> Tarea '{{name}}' registrada")
            except Exception as e: logger.error(f"❌ Error cargando tareas de {{module_name}}: {{e}}")

from core.streams import streams_manager
async def stream_consumer():
    await streams_manager.connect()
    logger.info("🌊 [STREAMS] Monitor de eventos activo...")
    while True:
        try:
            if os.path.exists(modules_path):
                for module_name in os.listdir(modules_path):
                    stream_name = f"{{module_name.lower()}}_events"
                    events = await streams_manager.consume_events(stream_name, count=5)
                    if events:
                        for _, msg_list in events:
                            for msg_id, data in msg_list:
                                rid = data.get("request_id", "STREAM")
                                token = request_id_ctx_var.set(rid)
                                logger.info(f"📢 [EVENTO] Detectado: {{data}}")
                                request_id_ctx_var.reset(token)
            await asyncio.sleep(2)
        except Exception: await asyncio.sleep(5)

async def on_startup(ctx):
    logger.info(f"🚀 {{APP_NAME}} Worker inicializado")
    asyncio.create_task(stream_consumer())

class WorkerSettings:
    functions = functions
    redis_settings = get_redis_settings("queue")
    on_startup = on_startup
    queue_name = os.getenv("QUEUE_NAME", "arq:queue")
    max_jobs = int(os.getenv("MAX_JOBS", 10))
"""
    with open(os.path.join(project_path, "worker.py"), "w") as f:
        f.write(worker_content)

def create_requirements(project_path, db_type):
    reqs = ["fastapi", "uvicorn[standard]", "pydantic", "python-dotenv", "httpx",
            "prometheus-fastapi-instrumentator", "sentry-sdk[fastapi]==2.44.0", "pytest", 
            "redis", "arq", "inquirer", "PyJWT", "cryptography", "tenacity"]
    if db_type in ["sql", "both"]: reqs += ["sqlalchemy", "asyncpg", "alembic", "pgvector"]
    if db_type in ["mongo", "both"]: reqs += ["motor"]
    if db_type == "excel": reqs += ["openpyxl"]
    with open(os.path.join(project_path, "requirements.txt"), "w") as f:
        f.write("\n".join(reqs) + "\n")

def create_dockerfile(project_path):
    content = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["sh", "-c", "export ENVIRONMENT=docker && uvicorn main:app --host 0.0.0.0 --port 8000"]
"""
    with open(os.path.join(project_path, "Dockerfile"), "w") as f:
        f.write(content)
