import os
import uuid

def create_env_files(project_path, db_type, base_port=8010, description="", use_iam=True):
    """Genera .env, .env.dev, .env.prod, .env.docker y sus ejemplos con puertos dinámicos."""
    
    # Cálculo de puertos derivados del base_port (Bloque de 10)
    api_port = base_port
    pg_port = base_port + 1
    pg_bouncer_port = base_port + 2
    redis_port = base_port + 3
    mongo_port = base_port + 4
    prom_port = base_port + 5
    grafana_port = base_port + 6

    def get_redis_vars(env):
        host = "redis" if env == "docker" else "localhost"
        r_port = 6379 if env == "docker" else redis_port
        return f"\n# Redis Especializado (Bases Lógicas 0, 1, 2)\nREDIS_CACHE_URL=redis://{host}:{r_port}/0\nREDIS_PUBSUB_URL=redis://{host}:{r_port}/1\nREDIS_QUEUE_URL=redis://{host}:{r_port}/2\n"

    def get_db_vars(env, db_type):
        host = "postgres" if env == "docker" else "localhost"
        p_port = 5432 if env == "docker" else pg_bouncer_port
        mhost = "mongo" if env == "docker" else "localhost"
        m_port = 27017 if env == "docker" else mongo_port
        res = ""
        if db_type in ["sql", "both"]:
            res += f"\n# SQL DB (PostgreSQL via PgBouncer)\nDATABASE_URL_DEV=postgresql+asyncpg://admin:password123@{host}:{p_port}/saas_db\nDATABASE_URL_PROD=\n"
        if db_type in ["mongo", "both"]:
            res += f"\n# NoSQL DB (MongoDB)\nMONGODB_URL_DEV=mongodb://admin:password123@{mhost}:{m_port}/\nMONGODB_DB_NAME=saas_db\nMONGODB_URL_PROD=\n"
        if db_type == "excel":
            res += f"\n# Excel Storage\nEXCEL_STORAGE_PATH=storage/{app_name.lower()}.xlsx\nEXCEL_SHEET_DEFAULT=sheet1\n"
        return res

    envs = ["dev", "prod", "docker"]
    app_name = os.path.basename(project_path)
    for env in envs:
        iam_url = "http://host.docker.internal:8000" if env == "docker" else "http://localhost:8000"
        common = f"""# Core
APP_NAME={app_name}
DESCRIPTION={description}
ENVIRONMENT={env}
API_PORT={api_port}
"""
        if use_iam:
            common += f"""AUTH_PUBLIC_KEY=""  # Pega aquí el contenido de public_key.pem de ApiIam
IAM_URL={iam_url}
API_IAM_URL={iam_url}
IAM_PROJECT_KEY=REPLACE_WITH_KEY_FROM_IAM
"""
        
        common += f"""INTERNAL_APP_KEY={uuid.uuid4().hex}
SENTRY_DSN=https://47036b8f72bfdf2c741b2d173838827c@o4511147272568832.ingest.us.sentry.io/4511148836454400
SENTRY_TRACES_SAMPLE_RATE=1.0
"""
        common += get_redis_vars(env)
        common += get_db_vars(env, db_type)
        
        # Reales
        with open(os.path.join(project_path, f".env.{env}"), "w") as f:
            f.write(common)
        # Ejemplos
        with open(os.path.join(project_path, f".env.{env}.example"), "w") as f:
            f.write(common)

    # .env Maestro (Configuraciones Globales y Fallbacks)
    with open(os.path.join(project_path, ".env"), "w") as f:
        f.write("# ARCHIVO MAESTRO - CONFIGURACIONES GLOBALES\n")
        f.write(f"# DESCRIPCION: {description}\n")
        f.write("ENVIRONMENT=dev\n")
        if use_iam:
            f.write(f"IAM_URL=http://localhost:8000\n")
            f.write("IAM_PROJECT_KEY=REPLACE_WITH_KEY_FROM_IAM\n")
        f.write(f"API_PORT={api_port}\n")
        f.write("SENTRY_DSN=https://47036b8f72bfdf2c741b2d173838827c@o4511147272568832.ingest.us.sentry.io/4511148836454400\n")
        f.write(f"POSTGRES_PORT={pg_port}\n")
        f.write(f"PGBOUNCER_PORT={pg_bouncer_port}\n")
        f.write(f"MONGO_PORT={mongo_port}\n")
        f.write(f"REDIS_PORT={redis_port}\n")
        f.write(f"PROMETHEUS_PORT={prom_port}\n")
        f.write(f"GRAFANA_PORT={grafana_port}\n")
        if db_type == "excel":
            f.write(f"EXCEL_STORAGE_PATH=storage/{app_name.lower()}.xlsx\n")
            f.write("EXCEL_SHEET_DEFAULT=sheet1\n")

def create_gitignore(project_path):
    """Genera el .gitignore profesional."""
    content = """# Secretos y Entorno
.env
.env.*
!.env.*.example

# Python y Virtualenv
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
dist/
build/
.venv/
.pytest_cache/
storage/*.xlsx
storage/*.xls
storage/*.xlsm
!storage/.gitkeep

# IDEs
.vscode/
.idea/

# Sistema y Otros
.DS_Store
Thumbs.db
.docker/

# CometaX security (RSA Keys)
*.pem
private_key.pem
public_key.pem
"""
    with open(os.path.join(project_path, ".gitignore"), "w") as f:
        f.write(content)
