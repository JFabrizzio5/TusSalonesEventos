#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-}"
TARGET_SERVICE="${2:-FrameworkTest}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_ROOT="/tmp/cometax-dev"

log() {
    printf '==> %s\n' "$*"
}

warn() {
    printf 'WARN: %s\n' "$*" >&2
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Uso:
  ./scripts/dev_stack.sh local [Servicio]
  ./scripts/dev_stack.sh docker [Servicio]
  ./scripts/dev_stack.sh stop-local [Servicio]
  ./scripts/dev_stack.sh stop-docker [Servicio]
  ./scripts/dev_stack.sh status [Servicio]

Por defecto el servicio es FrameworkTest.
EOF
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "Falta el comando '$1'."
}

docker_accessible() {
    docker info >/dev/null 2>&1
}

ensure_docker_access() {
    docker_accessible || die "Docker no está accesible. Inicia el daemon o revisa permisos del usuario."
}

replace_exact_line() {
    local file="$1"
    local old_line="$2"
    local new_line="$3"
    local tmp_file

    [[ -f "$file" ]] || return 0
    grep -Fqx "$old_line" "$file" || return 0

    tmp_file="$(mktemp)"
    awk -v old="$old_line" -v new="$new_line" '{ if ($0 == old) print new; else print }' "$file" >"$tmp_file"
    mv "$tmp_file" "$file"
}

set_key_value() {
    local file="$1"
    local key="$2"
    local value="$3"
    local tmp_file

    [[ -f "$file" ]] || return 0
    tmp_file="$(mktemp)"
    awk -v key="$key" -v value="$value" '
        index($0, key "=") == 1 { print key "=" value; found = 1; next }
        { print }
        END {
            if (!found) {
                print key "=" value
            }
        }
    ' "$file" >"$tmp_file"
    mv "$tmp_file" "$file"
}

get_key_value() {
    local file="$1"
    local key="$2"

    [[ -f "$file" ]] || return 0
    awk -F= -v key="$key" 'index($0, key "=") == 1 { print substr($0, length(key) + 2); exit }' "$file"
}

normalize_apiiam_env_file() {
    local file="$1"
    [[ -f "$file" ]] || return 0

    replace_exact_line "$file" "REDIS_CACHE_URL=redis://localhost:6379/0" "REDIS_CACHE_URL=redis://localhost:8003/0"
    replace_exact_line "$file" "REDIS_PUBSUB_URL=redis://localhost:6379/1" "REDIS_PUBSUB_URL=redis://localhost:8003/1"
    replace_exact_line "$file" "REDIS_QUEUE_URL=redis://localhost:6379/2" "REDIS_QUEUE_URL=redis://localhost:8003/2"
    replace_exact_line "$file" "DATABASE_URL_DEV=postgresql+asyncpg://admin:password123@localhost:6432/saas_db" "DATABASE_URL_DEV=postgresql+asyncpg://admin:password123@localhost:8002/saas_db"
    replace_exact_line "$file" "DATABASE_URL_DEV=postgresql+asyncpg://admin:password123@postgres:6432/saas_db" "DATABASE_URL_DEV=postgresql+asyncpg://admin:password123@postgres:5432/saas_db"

    set_key_value "$file" "API_PORT" "8000"
    set_key_value "$file" "POSTGRES_PORT" "8001"
    set_key_value "$file" "PGBOUNCER_PORT" "8002"
    set_key_value "$file" "REDIS_PORT" "8003"
    set_key_value "$file" "PROMETHEUS_PORT" "8005"
    set_key_value "$file" "GRAFANA_PORT" "8006"
}

normalize_apiiam_envs() {
    local dir="$1"
    normalize_apiiam_env_file "$dir/.env"
    normalize_apiiam_env_file "$dir/.env.dev"
    normalize_apiiam_env_file "$dir/.env.prod"
    normalize_apiiam_env_file "$dir/.env.dev.example"
    normalize_apiiam_env_file "$dir/.env.prod.example"
}

docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose "$@"
    else
        docker compose "$@"
    fi
}

service_dir() {
    printf '%s/%s' "$REPO_ROOT" "$1"
}

copy_if_missing() {
    local src="$1"
    local dst="$2"
    local display_path
    if [[ -f "$src" && ! -f "$dst" ]]; then
        cp "$src" "$dst"
        display_path="${dst#$REPO_ROOT/}"
        log "Creado $display_path desde ejemplo."
    fi
}

ensure_env_files() {
    local service="$1"
    local dir
    dir="$(service_dir "$service")"
    [[ -d "$dir" ]] || die "No existe el servicio '$service'."

    copy_if_missing "$dir/.env.dev.example" "$dir/.env.dev"
    copy_if_missing "$dir/.env.prod.example" "$dir/.env.prod"
    copy_if_missing "$dir/.env.docker.example" "$dir/.env.docker"
    copy_if_missing "$dir/.env.dev.example" "$dir/.env"

    if [[ "$service" == "ApiIam" ]]; then
        normalize_apiiam_envs "$dir"
    fi
}

load_ports() {
    local service="$1"
    unset API_PORT REDIS_PORT POSTGRES_PORT PGBOUNCER_PORT MONGO_PORT PROMETHEUS_PORT GRAFANA_PORT || true

    local dir env_file
    dir="$(service_dir "$service")"
    env_file="$dir/.env"

    API_PORT="$(get_key_value "$env_file" "API_PORT")"
    POSTGRES_PORT="$(get_key_value "$env_file" "POSTGRES_PORT")"
    PGBOUNCER_PORT="$(get_key_value "$env_file" "PGBOUNCER_PORT")"
    REDIS_PORT="$(get_key_value "$env_file" "REDIS_PORT")"
    MONGO_PORT="$(get_key_value "$env_file" "MONGO_PORT")"
    PROMETHEUS_PORT="$(get_key_value "$env_file" "PROMETHEUS_PORT")"
    GRAFANA_PORT="$(get_key_value "$env_file" "GRAFANA_PORT")"

    if [[ "$service" == "ApiIam" ]]; then
        API_PORT="${API_PORT:-8000}"
        POSTGRES_PORT="${POSTGRES_PORT:-8001}"
        PGBOUNCER_PORT="${PGBOUNCER_PORT:-8002}"
        REDIS_PORT="${REDIS_PORT:-8003}"
        PROMETHEUS_PORT="${PROMETHEUS_PORT:-8005}"
        GRAFANA_PORT="${GRAFANA_PORT:-8006}"
    elif [[ "$service" == "FrameworkTest" ]]; then
        API_PORT="${API_PORT:-8010}"
        POSTGRES_PORT="${POSTGRES_PORT:-8011}"
        PGBOUNCER_PORT="${PGBOUNCER_PORT:-8012}"
        REDIS_PORT="${REDIS_PORT:-8013}"
        MONGO_PORT="${MONGO_PORT:-8014}"
        PROMETHEUS_PORT="${PROMETHEUS_PORT:-8015}"
        GRAFANA_PORT="${GRAFANA_PORT:-8016}"
    else
        [[ -n "${API_PORT:-}" ]] || die "No pude inferir API_PORT para '$service'. Define los puertos en $env_file."
        POSTGRES_PORT="${POSTGRES_PORT:-$((API_PORT + 1))}"
        PGBOUNCER_PORT="${PGBOUNCER_PORT:-$((API_PORT + 2))}"
        REDIS_PORT="${REDIS_PORT:-$((API_PORT + 3))}"
        MONGO_PORT="${MONGO_PORT:-$((API_PORT + 4))}"
        PROMETHEUS_PORT="${PROMETHEUS_PORT:-$((API_PORT + 5))}"
        GRAFANA_PORT="${GRAFANA_PORT:-$((API_PORT + 6))}"
    fi

    export API_PORT REDIS_PORT POSTGRES_PORT PGBOUNCER_PORT MONGO_PORT PROMETHEUS_PORT GRAFANA_PORT
}

list_infra_services() {
    local service="$1"
    local dir
    dir="$(service_dir "$service")"
    load_ports "$service"
    (
        cd "$dir"
        docker_compose config --services | grep -vxE 'api|worker' || true
    )
}

start_infra() {
    local service="$1"
    local dir
    dir="$(service_dir "$service")"
    mapfile -t infra_services < <(list_infra_services "$service")

    if (( ${#infra_services[@]} == 0 )); then
        warn "No encontré servicios de infraestructura para '$service'."
        return
    fi

    load_ports "$service"
    (
        cd "$dir"
        log "Levantando infraestructura Docker de $service: ${infra_services[*]}"
        docker_compose up -d "${infra_services[@]}"
    )
}

stop_infra() {
    local service="$1"
    local dir
    dir="$(service_dir "$service")"
    if [[ ! -f "$dir/docker-compose.yml" ]]; then
        return
    fi
    ensure_env_files "$service"
    load_ports "$service"
    (
        cd "$dir"
        docker_compose down
    )
}

ensure_venv_bin() {
    local service="$1"
    local dir venv_bin
    dir="$(service_dir "$service")"
    venv_bin="$dir/venv/bin"
    [[ -x "$venv_bin/python" ]] || die "No encontré venv en $dir/venv. Instala dependencias del servicio primero."
    printf '%s' "$venv_bin"
}

service_runtime_dir() {
    local service="$1"
    printf '%s/%s' "$RUNTIME_ROOT" "$service"
}

pid_file() {
    local service="$1"
    local process_name="$2"
    printf '%s/pids/%s.pid' "$(service_runtime_dir "$service")" "$process_name"
}

log_file() {
    local service="$1"
    local process_name="$2"
    printf '%s/logs/%s.log' "$(service_runtime_dir "$service")" "$process_name"
}

prepare_runtime_dirs() {
    local service="$1"
    mkdir -p "$(service_runtime_dir "$service")/pids" "$(service_runtime_dir "$service")/logs"
}

is_pid_running() {
    local file="$1"
    [[ -f "$file" ]] && kill -0 "$(cat "$file")" 2>/dev/null
}

wait_for_http() {
    local url="$1"
    local label="$2"
    local attempts="${3:-30}"
    local i

    for ((i = 1; i <= attempts; i++)); do
        if curl -fsS "$url" >/dev/null 2>&1; then
            log "$label disponible en $url"
            return 0
        fi
        sleep 1
    done

    warn "No pude confirmar salud de $label en $url"
    return 1
}

run_migrations() {
    local service="$1"
    local dir venv_bin attempts
    dir="$(service_dir "$service")"

    if [[ ! -f "$dir/alembic.ini" ]]; then
        return
    fi

    venv_bin="$(ensure_venv_bin "$service")"
    attempts=10
    while (( attempts > 0 )); do
        if (
            cd "$dir"
            ENVIRONMENT=dev "$venv_bin/alembic" upgrade head
        ); then
            log "Migraciones OK para $service"
            return
        fi
        attempts=$((attempts - 1))
        sleep 2
    done

    die "Falló alembic upgrade head en $service"
}

start_local_process() {
    local service="$1"
    local process_name="$2"
    local dir="$3"
    shift 3

    local pid_path log_path
    pid_path="$(pid_file "$service" "$process_name")"
    log_path="$(log_file "$service" "$process_name")"

    if is_pid_running "$pid_path"; then
        log "$service/$process_name ya está corriendo (PID $(cat "$pid_path"))."
        return
    fi

    (
        cd "$dir"
        nohup "$@" >"$log_path" 2>&1 &
        echo $! >"$pid_path"
    )

    log "Iniciado $service/$process_name (PID $(cat "$pid_path"))"
}

start_local_service() {
    local service="$1"
    local dir venv_bin api_port
    dir="$(service_dir "$service")"
    venv_bin="$(ensure_venv_bin "$service")"
    prepare_runtime_dirs "$service"
    load_ports "$service"
    api_port="$API_PORT"

    run_migrations "$service"

    if [[ -f "$dir/main.py" ]]; then
        start_local_process \
            "$service" api "$dir" \
            env ENVIRONMENT=dev PYTHONUNBUFFERED=1 "$venv_bin/uvicorn" main:app --host 0.0.0.0 --port "$api_port"
    fi

    if [[ -f "$dir/worker.py" ]]; then
        start_local_process \
            "$service" worker "$dir" \
            env ENVIRONMENT=dev PYTHONUNBUFFERED=1 "$venv_bin/arq" worker.WorkerSettings
    fi
}

stop_local_process() {
    local service="$1"
    local process_name="$2"
    local pid_path
    pid_path="$(pid_file "$service" "$process_name")"

    if is_pid_running "$pid_path"; then
        kill "$(cat "$pid_path")"
        rm -f "$pid_path"
        log "Detenido $service/$process_name"
    elif [[ -f "$pid_path" ]]; then
        rm -f "$pid_path"
    fi
}

print_urls() {
    local service="$1"
    load_ports "$service"
    printf '    %s API: http://localhost:%s\n' "$service" "$API_PORT"
    printf '    %s Docs: http://localhost:%s/docs\n' "$service" "$API_PORT"
}

start_local_stack() {
    require_cmd docker
    require_cmd curl
    require_cmd python3
    ensure_docker_access

    ensure_env_files "ApiIam"
    start_infra "ApiIam"
    start_local_service "ApiIam"
    wait_for_http "http://localhost:8000/health" "ApiIam" || true

    if [[ "$TARGET_SERVICE" != "ApiIam" ]]; then
        ensure_env_files "$TARGET_SERVICE"
        start_infra "$TARGET_SERVICE"
        start_local_service "$TARGET_SERVICE"
        load_ports "$TARGET_SERVICE"
        wait_for_http "http://localhost:${API_PORT}/health" "$TARGET_SERVICE" || true
    fi

    log "Stack local listo."
    print_urls "ApiIam"
    if [[ "$TARGET_SERVICE" != "ApiIam" ]]; then
        print_urls "$TARGET_SERVICE"
    fi
    printf '    Logs locales: %s\n' "$RUNTIME_ROOT"
}

start_docker_stack() {
    require_cmd docker
    require_cmd curl
    ensure_docker_access

    ensure_env_files "ApiIam"
    load_ports "ApiIam"
    (
        cd "$(service_dir "ApiIam")"
        log "Levantando ApiIam completo en Docker"
        docker_compose up -d --build
    )
    wait_for_http "http://localhost:8000/health" "ApiIam" || true

    if [[ "$TARGET_SERVICE" != "ApiIam" ]]; then
        ensure_env_files "$TARGET_SERVICE"
        load_ports "$TARGET_SERVICE"
        (
            cd "$(service_dir "$TARGET_SERVICE")"
            log "Levantando $TARGET_SERVICE completo en Docker"
            docker_compose up -d --build
        )
        wait_for_http "http://localhost:${API_PORT}/health" "$TARGET_SERVICE" || true
    fi

    log "Stack Docker listo."
    print_urls "ApiIam"
    if [[ "$TARGET_SERVICE" != "ApiIam" ]]; then
        print_urls "$TARGET_SERVICE"
    fi
}

stop_local_stack() {
    stop_local_process "ApiIam" worker
    stop_local_process "ApiIam" api

    if [[ "$TARGET_SERVICE" != "ApiIam" ]]; then
        stop_local_process "$TARGET_SERVICE" worker
        stop_local_process "$TARGET_SERVICE" api
    fi

    if docker_accessible; then
        stop_infra "ApiIam"
        if [[ "$TARGET_SERVICE" != "ApiIam" ]]; then
            stop_infra "$TARGET_SERVICE"
        fi
    else
        warn "Docker no está accesible. Solo detuve procesos locales."
    fi
}

stop_docker_stack() {
    ensure_docker_access
    stop_infra "ApiIam"
    if [[ "$TARGET_SERVICE" != "ApiIam" ]]; then
        stop_infra "$TARGET_SERVICE"
    fi
}

status_stack() {
    local service process pid_path
    for service in ApiIam; do
        for process in api worker; do
            pid_path="$(pid_file "$service" "$process")"
            if is_pid_running "$pid_path"; then
                printf 'LOCAL %s/%s PID=%s\n' "$service" "$process" "$(cat "$pid_path")"
            fi
        done
    done

    if [[ "$TARGET_SERVICE" != "ApiIam" ]]; then
        for process in api worker; do
            pid_path="$(pid_file "$TARGET_SERVICE" "$process")"
            if is_pid_running "$pid_path"; then
                printf 'LOCAL %s/%s PID=%s\n' "$TARGET_SERVICE" "$process" "$(cat "$pid_path")"
            fi
        done
    fi

    if docker_accessible; then
        for service in ApiIam; do
            if [[ -f "$(service_dir "$service")/docker-compose.yml" ]]; then
                ensure_env_files "$service"
                load_ports "$service"
                (
                    cd "$(service_dir "$service")"
                    docker_compose ps
                )
            fi
        done

        if [[ "$TARGET_SERVICE" != "ApiIam" && -f "$(service_dir "$TARGET_SERVICE")/docker-compose.yml" ]]; then
            ensure_env_files "$TARGET_SERVICE"
            load_ports "$TARGET_SERVICE"
            (
                cd "$(service_dir "$TARGET_SERVICE")"
                docker_compose ps
            )
        fi
    else
        warn "Docker no está accesible. Omitiendo estado de contenedores."
    fi
}

main() {
    [[ -n "$MODE" ]] || {
        usage
        exit 1
    }

    case "$MODE" in
        local)
            start_local_stack
            ;;
        docker)
            start_docker_stack
            ;;
        stop-local)
            stop_local_stack
            ;;
        stop-docker)
            stop_docker_stack
            ;;
        status)
            status_stack
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main
