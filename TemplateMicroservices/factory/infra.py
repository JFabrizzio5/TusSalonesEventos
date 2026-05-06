import os

def create_docker_compose(project_path, project_name, db_type, docker_config=None):
    """Genera el docker-compose.yml con redes explícitas y configuraciones dinámicas desde IAM."""
    if not docker_config:
        docker_config = {}
        
    db_services = ""
    db_dependencies = ""
    volumes_section = ""

    # Valores dinámicos o defaults
    images = {
        "postgres": docker_config.get("postgres_image", "pgvector/pgvector:pg15"),
        "pgbouncer": docker_config.get("pgbouncer_image", "edoburu/pgbouncer:latest"),
        "mongo": docker_config.get("mongo_image", "mongo:latest"),
        "redis": docker_config.get("redis_image", "redis:alpine"),
        "prometheus": docker_config.get("prometheus_image", "prom/prometheus"),
        "grafana": docker_config.get("grafana_image", "grafana/grafana")
    }

    if db_type in ["sql", "both"]:
        db_services += f"""
  postgres:
    image: {images['postgres']}
    container_name: {project_name.lower()}_postgres
    networks: [saas_net]
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password123
      POSTGRES_DB: saas_db
    ports: ["${{POSTGRES_PORT:-5432}}:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d saas_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  pgbouncer:
    image: {images['pgbouncer']}
    container_name: {project_name.lower()}_pgbouncer
    networks: [saas_net]
    environment:
      DB_USER: admin
      DB_PASSWORD: password123
      DB_HOST: postgres
      DB_NAME: saas_db
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 500
      DEFAULT_POOL_SIZE: 20
    ports: ["${{PGBOUNCER_PORT:-6432}}:5432"]
    depends_on:
      postgres:
        condition: service_healthy
"""
        db_dependencies += """
      pgbouncer:
        condition: service_started"""
        volumes_section += "\n  postgres_data:"

    if db_type in ["mongo", "both"]:
        db_services += f"""
  mongo:
    image: {images['mongo']}
    container_name: {project_name.lower()}_mongo
    networks: [saas_net]
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
    ports: ["${{MONGO_PORT:-27017}}:27017"]
    volumes: [mongo_data:/data/db]
    healthcheck:
      test: ["CMD", "mongosh", "--quiet", "--eval", "db.adminCommand('ping')"]
      interval: 5s
      timeout: 5s
      retries: 5
"""
        db_dependencies += """
      mongo:
        condition: service_healthy"""
        volumes_section += "\n  mongo_data:"

    compose_content = f"""networks:
  saas_net:
    driver: bridge

services:
  api:
    build: .
    container_name: {project_name.lower()}_api
    networks: [saas_net]
    ports: ["${{API_PORT:-8000}}:8000"]
    env_file: [.env, .env.docker]
    volumes: [.:/app]
    command: >
      sh -c "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    depends_on:
      redis:
        condition: service_healthy{db_dependencies}

  worker:
    build: .
    container_name: {project_name.lower()}_worker
    networks: [saas_net]
    env_file: [.env.docker]
    volumes: [.:/app]
    command: arq worker.WorkerSettings
    depends_on:
      redis:
        condition: service_healthy{db_dependencies}

  redis:
    image: {images['redis']}
    container_name: {project_name.lower()}_redis
    networks: [saas_net]
    ports: ["${{REDIS_PORT:-6379}}:6379"]
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
{db_services}
  prometheus:
    image: {images['prometheus']}
    container_name: {project_name.lower()}_prometheus
    networks: [saas_net]
    extra_hosts: ["host.docker.internal:host-gateway"]
    volumes: [./prometheus.yml:/etc/prometheus/prometheus.yml]
    ports: ["${{PROMETHEUS_PORT:-9090}}:9090"]

  grafana:
    image: {images['grafana']}
    container_name: {project_name.lower()}_grafana
    networks: [saas_net]
    ports: ["${{GRAFANA_PORT:-3000}}:3000"]
    volumes: [./provisioning:/etc/grafana/provisioning]
    environment: [GF_SECURITY_ADMIN_PASSWORD=admin]
    depends_on: [prometheus]
"""
    if volumes_section:
        compose_content += f"\nvolumes:{volumes_section}\n"

    with open(os.path.join(project_path, "docker-compose.yml"), "w") as f:
        f.write(compose_content)

def create_alembic_setup(project_path):
    """Genera la configuración base para Alembic (Migraciones)."""
    # [Same as before, no changes needed to logic]
    ini_content = """[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic
[handlers]
keys = console
[formatters]
keys = generic
[logger_root]
level = WARN
handlers = console
qualname =
[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine
[logger_alembic]
level = INFO
handlers =
qualname = alembic
[handler_console]
class = StreamHandler
args = (sys.stdout,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
    with open(os.path.join(project_path, "alembic.ini"), "w") as f:
        f.write(ini_content)

    mig_path = os.path.join(project_path, "migrations")
    os.makedirs(mig_path, exist_ok=True)
    os.makedirs(os.path.join(mig_path, "versions"), exist_ok=True)

    env_content = """import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import os
import sys

sys.path.append(os.getcwd())
from config.database import ENVIRONMENT, Base

# --- AUTO-DISCOVERY DE MODELOS ---
def import_all_models():
    import importlib
    import os
    modules_path = os.path.join(os.getcwd(), "modules")
    if os.path.exists(modules_path):
        for module_name in os.listdir(modules_path):
            try:
                # Importamos el paquete 'models' para captar todo lo registrado en __init__.py
                importlib.import_module(f"modules.{module_name}.models")
            except ImportError:
                continue

import_all_models()
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    from dotenv import load_dotenv
    load_dotenv()
    suffix = f"_{ENVIRONMENT.upper()}" if ENVIRONMENT else "_DEV"
    return os.getenv(f"DATABASE_URL{suffix}") or os.getenv("DATABASE_URL_DEV")

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    connectable = async_engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
"""
    with open(os.path.join(mig_path, "env.py"), "w") as f:
        f.write(env_content)

    with open(os.path.join(mig_path, "script.py.mako"), "w") as f:
        f.write("""\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
""")
