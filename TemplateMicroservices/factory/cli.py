import os

def create_commands_py(project_path):
    """Genera el script interactivo commands.py con soporte Pro completo y ports dinámicos."""
    
    cli_content = r'''import os
import sys
import subprocess
import inquirer
import time
from dotenv import load_dotenv

# Cargar configuración actual
load_dotenv(".env")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
load_dotenv(f".env.{ENVIRONMENT}")

def run(cmd):
    try:
        subprocess.run(cmd, shell=True, check=False)
    except Exception as e:
        print(f"❌ Error: {e}")

def has_sql_support():
    return bool(os.getenv("DATABASE_URL_DEV") or os.getenv("DATABASE_URL_PROD"))

def has_excel_support():
    return bool(os.getenv("EXCEL_STORAGE_PATH"))

def get_project_info():
    api_port = os.getenv("API_PORT", "8000")
    redis_port = os.getenv("REDIS_PORT", "6379")
    excel_path = os.getenv("EXCEL_STORAGE_PATH")
    print(f"""
🚀 Información del Microservicio:
-----------------------------------------
🌍 API: http://localhost:{api_port}
📜 Swagger/Docs: http://localhost:{api_port}/docs
📊 Queue Stats: http://localhost:{api_port}/queue/stats
📈 Metrics: http://localhost:{api_port}/metrics
⚡ Redis Port (Host): {redis_port}
-----------------------------------------
Ambiente Activo: {ENVIRONMENT}
""")
    if excel_path:
        print(f"📗 Excel Storage: {excel_path}")
    # Auto-discovery de módulos y sus endpoints
    modules_path = "modules"
    if os.path.exists(modules_path):
        print("🧩 Módulos y Endpoints Registrados:")
        for mod in os.listdir(modules_path):
            mod_path = os.path.join(modules_path, mod)
            if os.path.isdir(mod_path) and not mod.startswith("__"):
                api_dir = os.path.join(mod_path, "api")
                if os.path.exists(api_dir):
                    for v in os.listdir(api_dir):
                        v_path = os.path.join(api_dir, v)
                        if os.path.isdir(v_path) and not v.startswith("__"):
                            base_url = f"http://localhost:{api_port}/{mod.lower()}/{v}"
                            print(f"  📦 {mod} ({v}):")
                            print(f"     ✅ Status: {base_url}/status")
                            # Detectar features en routes.py
                            route_file = os.path.join(v_path, "routes.py")
                            if os.path.exists(route_file):
                                with open(route_file, "r") as f:
                                    routes_content = f.read()
                                    if "test-queue" in routes_content: print(f"     ⚡ Queue:  {base_url}/test-queue")
                                    if "test-events" in routes_content: print(f"     📢 Events: {base_url}/test-events")
                                    if "test-cache" in routes_content: print(f"     ❄️  Cache:  {base_url}/test-cache")
        print("-----------------------------------------")

def show_api_logs():
    print(f"🔍 Mostrando logs (CTRL+C para salir)...")
    run(f"docker-compose logs -f api")

class ModuleManager:
    @staticmethod
    def get_existing_modules():
        modules_path = "modules"
        if not os.path.exists(modules_path):
            return []
        return [d for d in os.listdir(modules_path) if os.path.isdir(os.path.join(modules_path, d)) and not d.startswith("__")]

    @staticmethod
    def validate_infra():
        print("\n🔍 Validando Infraestructura (Paciencia, comprobando puertos específicos)...")
        import redis
        # Leer el puerto real del .env
        r_port = os.getenv("REDIS_PORT", "6379")
        urls_to_try = [
            f"redis://localhost:{r_port}/1",
            os.getenv("REDIS_URL", f"redis://redis:6379/1")
        ]
        
        max_retries = 3
        connected = False
        for attempt in range(max_retries):
            for url in urls_to_try:
                try:
                    r = redis.from_url(url, socket_connect_timeout=3)
                    r.ping()
                    print(f"✅ Redis: Conectado ({url})")
                    connected = True
                    break
                except: continue
            if connected: break
            if attempt < max_retries - 1:
                print(f"⏳ Reintentando conexión local en puerto {r_port} ({attempt + 1}/{max_retries})...")
                time.sleep(2)
        
        if not connected:
            print(f"❌ Redis: No detectado en puerto {r_port}. ¿Ya corriste Docker Up?")
        return connected

    @staticmethod
    def create_module_wizard():
        existing = ModuleManager.get_existing_modules()
        choices = [
            ('✨ Crear Nuevo Módulo', 'new'),
            ('➕ Añadir Model (make:model)', 'make_model'),
            ('➕ Añadir Repository (make:repo)', 'make_repo'),
            ('➕ Añadir API/Router (make:api)', 'make_api'),
            ('➕ Añadir Seeder (make:seeder)', 'make_seeder'),
            ('➕ Añadir Service Wrapper (make:service)', 'make_service'),
            ('⚙️ Configurar Existente', 'config_existing')
        ]
        
        questions = [inquirer.List('action', message="Gestión de Módulos", choices=choices)]
        answer = inquirer.prompt(questions)
        if not answer: return

        if answer['action'] == 'new':
            name = input("Nombre del módulo: ").strip()
            if not name: return
            version = input("Versión (v1): ") or "v1"
            feat_qs = [inquirer.Checkbox('features', message="Features", choices=[
                ('🔌 WS', 'ws'), ('📦 Queues', 'queues'), ('📢 Streams', 'pubsub'), ('⚡ Cache', 'cache')
            ])]
            feats = inquirer.prompt(feat_qs)['features'] or []
            
            queue_name, max_jobs = "default", "10"
            if 'queues' in feats:
                queue_name = input("Nombre de la cola: ") or "default"
                max_jobs = input("Max Jobs: ") or "10"

            ModuleManager.generate_module_structure(name, version, feats, queue_name, max_jobs)
            ModuleManager.validate_infra()
            
        elif answer['action'] == 'config_existing':
            choices_mod = [(f'📦 {mod}', mod) for mod in existing]
            ans_mod = inquirer.prompt([inquirer.List('module', message="Selecciona el módulo", choices=choices_mod)])
            if not ans_mod: return
            mod_name = ans_mod['module']
            sub_qs = [inquirer.List('sub_action', message=f"Configurar {mod_name}", choices=[
                ('🔌 WS', 'ws'), ('📦 Queues', 'queues'), ('📢 Streams', 'pubsub'), ('⚡ Cache', 'cache'), ('🔙 Volver', 'back')
            ])]
            sub_ans = inquirer.prompt(sub_qs)
            if sub_ans and sub_ans['sub_action'] != 'back':
                ModuleManager.generate_module_structure(mod_name, "v1", [sub_ans['sub_action']])
                ModuleManager.validate_infra()

        elif answer['action'] in ['make_model', 'make_repo', 'make_api', 'make_seeder']:
            choices_mod = [(f'📦 {mod}', mod) for mod in existing]
            ans_mod = inquirer.prompt([inquirer.List('module', message="Módulo destino", choices=choices_mod)])
            if not ans_mod: return
            mod = ans_mod['module']
            
            if answer['action'] == 'make_model':
                name = input("Nombre del Modelo (ej. UserRole): ").strip()
                m_type = inquirer.prompt([inquirer.List('mtype', message="Tipo de Modelo", choices=[
                    ('🗄️ SQL (Tabla)', 'sql'), ('📝 Datos (Pydantic)', 'pydantic')
                ])])['mtype']
                
                filename = input("Nombre de archivo (default: models.py): ").strip() or "models.py"
                if not filename.endswith(".py"): filename += ".py"
                
                table = None
                if m_type == 'sql':
                    table = input(f"Nombre de tabla (default: {name.lower()}s): ").strip() or f"{name.lower()}s"
                
                ModuleManager.make_model(mod, name, m_type, filename, table)
            elif answer['action'] == 'make_repo':
                name = input("Nombre del Modelo para el Repo: ").strip()
                ModuleManager.make_repository(mod, name)
            elif answer['action'] == 'make_api':
                version = input("Versión (default: v1): ").strip() or "v1"
                subfolder = input("Subcarpeta opcional (ej. admin): ").strip()
                name = input("Nombre del archivo (ej. internal_routes): ").strip() or "routes"
                if not name.endswith(".py"): name += ".py"
                ModuleManager.make_api(mod, version, subfolder, name)
            elif answer['action'] == 'make_service':
                service_to_call = input("Nombre del microservicio destino (ej. payments): ").strip()
                if service_to_call:
                    ModuleManager.make_service_wrapper(mod, service_to_call)
            elif answer['action'] == 'make_seeder':
                table = input("Nombre de la tabla/entidad a poblar: ").strip()
                ModuleManager.make_seeder(mod, table)

    @staticmethod
    def make_model(module, name, m_type, filename, table=None):
        base = f"modules/{module.lower()}/models"
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, filename)
        
        content = ""
        # Si el archivo no existe, añadir cabecera
        if not os.path.exists(path):
            if m_type == 'sql':
                content += "from sqlalchemy import Column, Integer, String, DateTime, Boolean\nfrom config.database import Base\nfrom datetime import datetime\n"
            else:
                content += "from pydantic import BaseModel\nfrom typing import Optional, List\n"

        if m_type == 'sql':
            content += f"\nclass {name}(Base):\n    __tablename__ = \"{table}\"\n    id = Column(Integer, primary_key=True, index=True)\n    created_at = Column(DateTime, default=datetime.utcnow)\n"
        else:
            content += f"\nclass {name}(BaseModel):\n    # TODO: Añadir campos Pydantic\n    name: str\n"

        with open(path, "a") as f: f.write(content)
        
        # Auto-importar en __init__.py si no es el principal o para centralizar
        init_path = os.path.join(base, "__init__.py")
        module_file = filename.replace(".py", "")
        import_line = f"from . {module_file} import {name}\n"
        
        # Leer para evitar duplicados
        already_imported = False
        if os.path.exists(init_path):
            with open(init_path, "r") as f:
                if f"import {name}" in f.read(): already_imported = True
        
        if not already_imported:
            with open(init_path, "a") as f: f.write(import_line)
            print(f"🔗 Auto-importado {name} en {init_path}")

        print(f"✅ Modelo {name} ({m_type}) añadido a {path}")

    @staticmethod
    def make_repository(module, name):
        base = f"modules/{module.lower()}/repositories"
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, f"{name.lower()}_repository.py")
        content = f"""from sqlalchemy.ext.asyncio import AsyncSession
from modules.{module.lower()}.models.models import {name}
from sqlalchemy import select

class {name}Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select({name}))
        return result.scalars().all()
"""
        with open(path, "w") as f: f.write(content)
        print(f"✅ Repository creado en {path}")

    @staticmethod
    def make_api(module, version, subfolder, filename):
        base = f"modules/{module.lower()}/api/{version}"
        if subfolder: base = os.path.join(base, subfolder)
        os.makedirs(base, exist_ok=True)
        open(os.path.join(base, "__init__.py"), "a").close()
        
        path = os.path.join(base, filename)
        content = f"""from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_sql_db
from core.auth import get_current_user # 🔐 Importación de Auth Distribuido

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    return {{"msg": "API {filename} working in {module}/{version}"}}

# 🔐 Ejemplo de Ruta Protegida:
# @router.get("/me")
# async def read_users_me(current_user: dict = Depends(get_current_user)):
#     return current_user
"""
        with open(path, "w") as f: f.write(content)

    @staticmethod
    def make_service_wrapper(module, service_to_call):
        """Genera un wrapper pre-configurado para llamar a otro microservicio."""
        base = f"modules/{module.lower()}/services"
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, f"{service_to_call.lower()}_client.py")
        
        content = f"""from core.internal_client import get_service_client
import logging

logger = logging.getLogger("{service_to_call.lower()}_client")

class {service_to_call.capitalize()}Client:
    \"\"\"Wrapper para comunicarse con el microservicio {service_to_call.upper()}\"\"\"
    def __init__(self):
        self.client = get_service_client("{service_to_call.upper()}")

    async def get_status(self):
        \"\"\"Ejemplo de llamada: GET /health\"\"\"
        try:
            response = await self.client.get("/health")
            return response.json()
        except Exception as e:
            logger.error(f"Error llamando a {service_to_call.upper()}: {{e}}")
            return {{"status": "error", "detail": str(e)}}

# Instancia global para el módulo {module}
{service_to_call.lower()}_client = {service_to_call.capitalize()}Client()
"""
        with open(path, "w") as f: f.write(content)
        print(f"🚀 Wrapper de servicio para {service_to_call.upper()} creado en {path}")
        
        # Auto-registro en el routes.py principal
        main_routes = f"modules/{module.lower()}/api/{version}/routes.py"
        if os.path.exists(main_routes):
            import_name = filename.replace(".py", "")
            if subfolder:
                ref = f"from . {subfolder}.{import_name} import router as {import_name}_router"
            else:
                ref = f"from . {import_name} import router as {import_name}_router"
            
            with open(main_routes, "a") as f:
                f.write(f"\n# Auto-registered router\n{ref}\nrouter.include_router({import_name}_router, prefix=\"/{subfolder or import_name}\")\n")
            print(f"✅ API creada y registrada en {main_routes}")
        else:
            print(f"✅ API creada en {path} (Mantenlo registrado manualmente)")

    @staticmethod
    def make_seeder(module, table):
        base = f"modules/{module.lower()}/seeds"
        os.makedirs(base, exist_ok=True)
        open(os.path.join(base, "__init__.py"), "a").close()
        path = os.path.join(base, f"{table}_seed.py")
        content = f"""import logging
from sqlalchemy.ext.asyncio import AsyncSession
# from modules.{module.lower()}.models.models import {table.capitalize()}

logger = logging.getLogger("seeder_{module}")

async def seed(session: AsyncSession):
    logger.info("🌱 Sembrando datos para {module}:{table}...")
    # session.add({table.capitalize()}(...))
    # await session.commit()
"""
        with open(path, "w") as f: f.write(content)
        print(f"✅ Seeder creado en {path}")

    @staticmethod
    def generate_module_structure(name, version, feats, queue_name="default", max_jobs=10):
        from module_helper import capitalize_name
        name_clean = capitalize_name(name)
        base = f"modules/{name_clean.lower()}"
        folders = [f"{base}/api/{version}", f"{base}/models", f"{base}/repositories", f"{base}/services", f"{base}/internal", f"{base}/tests"]
        for fd in folders: os.makedirs(fd, exist_ok=True)
        for root, dirs, files in os.walk(base):
            for d in dirs: open(os.path.join(root, d, "__init__.py"), "a").close()
        open(f"{base}/__init__.py", "a").close()

        # Garantizar que modules/__init__.py existe
        modules_init = "modules/__init__.py"
        if not os.path.exists(modules_init):
            open(modules_init, "a").close()

        route_path = f"{base}/api/{version}/routes.py"
        if not os.path.exists(route_path):
            route_tpl = f"""import logging
from fastapi import APIRouter, Request
from core.trace import request_id_ctx_var

logger = logging.getLogger("{name_clean.lower()}_api")
router = APIRouter()

@router.get("/status")
async def status():
    return {{"module": "{name_clean}", "status": "online", "version": "{version}"}}
"""
            if 'queues' in feats:
                route_tpl += f"""
@router.get("/test-queue")
async def test_queue():
    from arq import create_pool
    from config.redis_config import get_redis_settings
    redis = await create_pool(get_redis_settings("queue"))
    rid = request_id_ctx_var.get()
    logger.info(f"📤 [{{rid}}] TAREA ENVIADA (Background) -> {name_clean}. Revisa logs del worker.")
    await redis.enqueue_job("process_{name_clean.lower()}_task", data="ping", request_id=rid)
    return {{"status": "task_enqueued", "queue": "{queue_name}", "request_id": rid, "detail": "Ver logs del worker para progreso"}}
"""
            if 'pubsub' in feats:
                route_tpl += f"""
@router.get("/test-events")
async def test_events():
    from core.streams import streams_manager
    rid = request_id_ctx_var.get()
    logger.info(f"📢 [{{rid}}] Enviando evento a stream {name_clean.lower()}_events...")
    await streams_manager.add_event("{name_clean.lower()}_events", {{"msg": "test", "request_id": rid}})
    return {{"status": "stream_sent", "request_id": rid}}
"""
            if 'cache' in feats:
                route_tpl += f"""
@router.get("/test-cache")
async def test_cache():
    from core.cache import cache_manager
    @cache_manager.cached(ttl=10)
    async def get_val():
        return {{"val": "cache-hit"}}
    return await get_val()
"""
            with open(route_path, "w") as f:
                f.write(route_tpl)

        # Scaffolding Pro (Enums, Errors)
        with open(f"{base}/enums.py", "w") as f:
            f.write(f"from enum import Enum\n\nclass {name_clean}ErrorCode(str, Enum):\n    NOT_FOUND = '{name_clean.upper()}_NOT_FOUND'")
        
        with open(f"{base}/errors.py", "w") as f:
            f.write(f"from fastapi import HTTPException\nfrom .enums import {name_clean}ErrorCode\n\nclass {name_clean}Error(HTTPException): pass")
        
        if 'queues' in feats:
            with open(f"{base}/services/tasks.py", "w") as f:
                f.write(f"""import logging
import asyncio
import time
import sentry_sdk
from core.trace import request_id_ctx_var
from core.monitor import monitor_manager

logger = logging.getLogger('{name_clean.lower()}_tasks')

async def process_{name_clean.lower()}_task(ctx, data: str, request_id: str = 'CORE'):
    token = request_id_ctx_var.set(request_id)
    start_time = time.time()
    await monitor_manager.connect() # Asegurar conexión
    try:
        msg_start = f'🚀 [{{request_id}}] INICIANDO -> {name_clean}: {{data}}'
        logger.info(msg_start)
        sentry_sdk.capture_message(msg_start, level="info")

        await asyncio.sleep(1) # Simulación de trabajo

        duration = time.time() - start_time
        msg_end = f'✅ [{{request_id}}] COMPLETADO -> {name_clean} ({{duration:.2f}}s)'
        logger.info(msg_end)
        sentry_sdk.capture_message(msg_end, level="info")
        await monitor_manager.report_success()
        return True
    except Exception as e:
        msg_error = f'❌ [{{request_id}}] FALLIDO -> {name_clean}: {{e}}'
        logger.error(msg_error)
        sentry_sdk.capture_exception(e)
        await monitor_manager.report_failure()
        raise
    finally:
        request_id_ctx_var.reset(token)""")
        print(f"✨ Módulo {name_clean} procesado.")
        api_port = os.getenv("API_PORT", "8000")
        base_url = f"http://localhost:{api_port}/{name_clean.lower()}/{version}"
        print(f"🌍 API Módulo ({version}):")
        print(f"  ✅ Status: {base_url}/status")
        if 'queues' in feats: print(f"  ⚡ Queue:  {base_url}/test-queue")
        if 'pubsub' in feats: print(f"  📢 Events: {base_url}/test-events")
        if 'cache' in feats:  print(f"  ❄️  Cache:  {base_url}/test-cache")
        print("-----------------------------------------")

def manage_migrations():
    if not has_sql_support():
        print("⚠️ Este proyecto no tiene backend SQL configurado. Las migraciones Alembic no aplican aquí.")
        return
    questions = [inquirer.List('action', message="Migraciones", choices=[
        ('Crear', 'create'), 
        ('Upgrade', 'upgrade'), 
        ('Rollback (Downgrade -1)', 'downgrade'),
        ('Back', 'back')
    ])]
    ans = inquirer.prompt(questions)
    if ans and ans['action'] == 'create':
        msg = input("Mensaje: ")
        run(f"docker-compose exec api alembic revision --autogenerate -m '{msg}'")
    elif ans and ans['action'] == 'upgrade': 
        run("docker-compose exec api alembic upgrade head")
    elif ans and ans['action'] == 'downgrade':
        run("docker-compose exec api alembic downgrade -1")

def main_menu():
    questions = [inquirer.List('option', message="Acción", choices=[
        ('🚀 Docker Up', 'up'), ('🛑 Docker Down', 'down'), ('📜 Logs', 'logs'), ('🏗️ Build', 'build'),
        ('🌱 Seed Data', 'seed'), ('📦 Módulos', 'module'), ('🔄 Migraciones', 'migrate'), 
        ('📊 Queue Stats', 'qstats'), ('🎯 Test Sentry', 'sentry'), ('🧪 Health', 'test'), 
        ('💥 Force Crash', 'crash'), ('ℹ️ Info & Config', 'info'), 
        ('♻️  Factory Reset (PELIGRO)', 'reset'), ('🚪 Salir', 'exit')
    ])]
    ans = inquirer.prompt(questions); option = ans['option'] if ans else 'exit'
    if option == 'up': run("docker-compose up -d --build"); get_project_info()
    elif option == 'down': run("docker-compose down")
    elif option == 'logs': show_api_logs()
    elif option == 'build': run("docker-compose build")
    elif option == 'seed':
        if not os.path.exists("seed.py"):
            print("⚠️ Este proyecto no incluye seed.py. Usa endpoints o scripts propios para poblar datos.")
        else:
            run("docker-compose exec api python3 seed.py")
    elif option == 'module': ModuleManager.create_module_wizard()
    elif option == 'migrate': manage_migrations()
    elif option == 'reset':
        confirm = inquirer.confirm("¿ESTÁS SEGURO? Se borrará TODO (DB + Migraciones).", default=False)
        if confirm:
            print("🧨 Iniciando Factory Reset...")
            run("docker-compose down -v")
            run("rm -rf migrations/versions/[0-9a-f]*.py")
            print("✅ Limpieza completada. Usa 'Docker Up' y luego crea una nueva migración inicial.")
    elif option == 'sentry': 
        api_port = os.getenv("API_PORT", "8000")
        run(f"curl http://localhost:{api_port}/test-metrics")
    elif option == 'test': 
        api_port = os.getenv("API_PORT", "8000")
        run(f"curl http://localhost:{api_port}/health")
    elif option == 'crash':
        print("💥 Forzando crash en contenedor...")
        run("docker-compose exec api kill -9 1")
    elif option == 'qstats':
        api_port = os.getenv("API_PORT", "8000")
        run(f"curl http://localhost:{api_port}/queue/stats")
    elif option == 'info': get_project_info()
    elif option == 'exit': sys.exit()

class module_helper:
    @staticmethod
    def capitalize_name(name): return "".join(word.capitalize() for word in name.split())
import sys
sys.modules['module_helper'] = module_helper

if __name__ == "__main__":
    while True:
        try: main_menu()
        except KeyboardInterrupt: sys.exit()
'''
    with open(os.path.join(project_path, "commands.py"), "w") as f:
        f.write(cli_content)

def create_run_sh(project_path):
    """Genera un run.sh robusto."""
    content = r"""#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"
if [ -d "./venv" ]; then
    source ./venv/bin/activate
    python3 commands.py
else
    python3 commands.py
fi
"""
    path = os.path.join(project_path, "run.sh")
    with open(path, "w") as f:
        f.write(content)
    try:
        os.chmod(path, 0o755)
    except:
        pass
