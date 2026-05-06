import os
import sys
import time
import subprocess
import threading
import itertools
from typing import Optional

# Monocromático Neón (Aesthetic B&W)
BOLD = "\033[1m"
DIM = "\033[2m"
WHITE_NEON = "\033[1;97m"  # Blanco brillante
GRAY_NEON = "\033[1;30m"   # Gris oscuro brillante
LIGHT_GRAY = "\033[0;37m"  # Gris claro normal
RESET = "\033[0m"

BANNER = f"""{WHITE_NEON}
 ▗▄▄▖ ▗▄▖ ▗▖  ▗▖▗▄▄▄▖▗▄▄▄▖ ▗▄▖ ▗▖  ▗▖
▐▌   ▐▌ ▐▌▐▛▚▞▜▌▐▌     █  ▐▌ ▐▌ ▝▚▞▘ 
▐▌   ▐▌ ▐▌▐▌  ▐▌▐▛▀▀▘  █  ▐▛▀▜▌  ▐▌  
▝▚▄▄▖▝▚▄▞▘▐▌  ▐▌▐▙▄▄▖  █  ▐▌ ▐▌▗▞▘▝▚▖
{GRAY_NEON}----------------------------------------
{LIGHT_GRAY}       C O M E T A X . C L I K
{GRAY_NEON}----------------------------------------{RESET}
"""

def print_help():
    print(BANNER)
    print(f" {BOLD}Usage:{RESET} cometax <command> [args]\n")
    print(f" {WHITE_NEON}Commands:{RESET}")
    print(f"  {WHITE_NEON}new{RESET}                   Crea un nuevo microservicio interactivo")
    print(f"  {WHITE_NEON}install{RESET} {DIM}<pkg>{RESET}         Instala pip local y lo agrega a requirements.txt")
    print(f"  {WHITE_NEON}freeze{RESET}                Congela las dependencias del proyecto a requirements.txt")
    print(f"  {WHITE_NEON}projects{RESET}              Lista los microservicios descubiertos en el directorio")
    print(f"  {WHITE_NEON}go{RESET}                    Abre el teletransportador (selector interactivo para hacer cd al proyecto)")
    print(f"  {WHITE_NEON}run{RESET} {DIM}[project]{RESET}           Levanta los contenedores (docker-compose up -d / sail up -d)")
    print(f"  {WHITE_NEON}down{RESET} {DIM}[project]{RESET}          Detiene los contenedores del proyecto")
    print(f"  {WHITE_NEON}shell{RESET} {DIM}[project]{RESET}         Abre una terminal dentro del contenedor principal")
    print(f"  {WHITE_NEON}module{RESET} {DIM}[name]{RESET}           Crea un nuevo módulo en el proyecto actual")
    print(f"  {WHITE_NEON}migrate{RESET}                  Ejecuta migraciones de la base de datos (Alembic / Artisan)")
    print(f"  {WHITE_NEON}seed{RESET}                     Ejecuta los seeders (Artisan)")
    print(f"  {WHITE_NEON}queue{RESET}                    Inicia el worker de colas (Artisan queue:work)")
    print(f"  {WHITE_NEON}test{RESET}                     Ejecuta las pruebas (Pytest / Artisan test)")
    print(f"  {WHITE_NEON}[artisan command]{RESET}        Cualquier comando de Artisan (Ej: cometax make:job EmailJob)")
    print("")

def animate_loading(stop_event, message="Cargando..."):
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stop_event.is_set():
        sys.stdout.write(f"\r{WHITE_NEON}[{next(spinner)}]{RESET} {LIGHT_GRAY}{message}{RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f"\r{' ' * (len(message) + 5)}\r")

def get_target_directory():
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, "venv")) or os.path.exists(os.path.join(cwd, ".env")):
        return cwd
        
    print(f"\n{BOLD}[!]{RESET} No estás dentro de la carpeta de un microservicio.")
    print(f"{GRAY_NEON}Selecciona el proyecto objetivo:{RESET}\n")
    
    projects = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for item in os.listdir(base_dir):
        path = os.path.join(base_dir, item)
        if os.path.isdir(path) and not item.startswith('.') and not item == '__pycache__':
            if os.path.exists(os.path.join(path, ".env")):
                projects.append(item)
                
    if not projects:
        print(f"{WHITE_NEON}[X]{RESET} No se encontraron microservicios. Abortando.")
        sys.exit(1)
        
    for idx, name in enumerate(projects, 1):
        print(f" {GRAY_NEON}{idx}{RESET} /// {WHITE_NEON}{name}{RESET}")
        
    try:
        ans = input(f"\n{WHITE_NEON}> {RESET}")
        idx = int(ans) - 1
        if 0 <= idx < len(projects):
            return os.path.join(base_dir, projects[idx])
    except:
        pass
        
    print(f"{WHITE_NEON}[X]{RESET} Selección inválida. Abortando.")
    sys.exit(1)

def get_project_dir_by_name(name: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, name)
    if os.path.isdir(path) and os.path.exists(os.path.join(path, ".env")):
        return path
    return None

def detect_venv_pip(base_dir=None):
    if not base_dir:
        base_dir = os.getcwd()
    
    # Detect Laravel (artisan exists)
    if os.path.exists(os.path.join(base_dir, "artisan")):
        sail_path = os.path.join(base_dir, "vendor", "bin", "sail")
        return "laravel", sail_path if os.path.exists(sail_path) else "composer"
        
    # Detect Python
    pip_path = os.path.join(base_dir, "venv", "bin", "pip")
    if not os.path.exists(pip_path):
         pip_path = os.path.join(base_dir, "venv", "Scripts", "pip")
    return "python", pip_path if os.path.exists(pip_path) else "pip"

def cmd_new():
    # Import launcher main and run it
    print(f"{WHITE_NEON}:: LOADING COMETAX ARCHITECTURE ::{RESET}")
    time.sleep(0.5)
    
    # Asegurar que launcher esté en sys.path
    cli_dir = os.path.dirname(os.path.abspath(__file__))
    if cli_dir not in sys.path:
        sys.path.insert(0, cli_dir)
        
    try:
        import launcher
        # Launcher runs its own input processes
        print(f"\n{GRAY_NEON}----------------------------------------{RESET}\n")
        launcher.main()
    except Exception as e:
        print(f"\n{BOLD}[!]{RESET} Error lanzando el creador: {e}")

def cmd_install(pkg_name: str):
    if not pkg_name:
        print(f"{BOLD}[X]{RESET} Debes proveer un nombre de paquete. Ej: {WHITE_NEON}cometax install fastapi{RESET}")
        return

    target_dir = get_target_directory()
    print(f"\n{GRAY_NEON}>_ PREPARANDO ENTORNO EN: {os.path.basename(target_dir)}{RESET}")
    env_type, cmd_exe = detect_venv_pip(target_dir)
    
    stop_event = threading.Event()
    th = threading.Thread(target=animate_loading, args=(stop_event, f"Instalando {WHITE_NEON}{pkg_name}{LIGHT_GRAY}..."))
    th.start()
    
    try:
        if env_type == "laravel":
            # Si usamos sail, el comando es "sail composer require <pkg>"
            # Si es composer crudo, es "composer require <pkg>"
            args = [cmd_exe, "composer", "require", pkg_name] if "sail" in cmd_exe else [cmd_exe, "require", pkg_name]
        else:
            args = [cmd_exe, "install", pkg_name]
            
        result = subprocess.run(args, capture_output=True, text=True, cwd=target_dir)
        stop_event.set()
        th.join()
        
        if result.returncode == 0:
            print(f"{WHITE_NEON}[+]{RESET} Dependencia '{pkg_name}' instalada exitosamente en {os.path.basename(target_dir)}.")
            if env_type == "python":
                cmd_freeze(target_dir)
        else:
            print(f"{WHITE_NEON}[X]{RESET} Falló la instalación de '{pkg_name}'.")
            print(f"{DIM}{result.stderr}{RESET}")
    except Exception as e:
        stop_event.set()
        th.join()
        print(f"{WHITE_NEON}[X]{RESET} Error ejecutando pip: {e}")

def cmd_freeze(target_dir=None):
    if not target_dir:
        target_dir = get_target_directory()
        
    env_type, cmd_exe = detect_venv_pip(target_dir)
    
    if env_type == "laravel":
        print(f"\n{GRAY_NEON}🚀 Info:{RESET} En Laravel las dependencias ya son auto-gestionadas por {WHITE_NEON}composer.json{RESET} y {WHITE_NEON}composer.lock{RESET}.")
        return
        
    req_file = os.path.join(target_dir, "requirements.txt")
    
    stop_event = threading.Event()
    th = threading.Thread(target=animate_loading, args=(stop_event, "Congelando dependencias..."))
    th.start()
    
    try:
        result = subprocess.run([cmd_exe, "freeze"], capture_output=True, text=True, cwd=target_dir)
        stop_event.set()
        th.join()
        
        if result.returncode == 0:
            with open(req_file, "w") as f:
                f.write(result.stdout)
            print(f"{WHITE_NEON}[+]{RESET} requirements.txt ha sido actualizado en {os.path.basename(target_dir)}.")
        else:
            print(f"{WHITE_NEON}[X]{RESET} Falló el pip freeze.")
    except Exception as e:
        stop_event.set()
        th.join()
        print(f"{WHITE_NEON}[X]{RESET} Error: {e}")

def cmd_projects():
    print(f"\n{WHITE_NEON}:: COMETAX ENVIRONMENT MAP ::{RESET}")
    print(f"{GRAY_NEON}Buscando microservicios...{RESET}")
    
    # Discovery recursivo ignorando carpetas pesadas/internas
    projects = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ignore_dirs = {'.git', 'vendor', 'venv', 'node_modules', '__pycache__', '.pytest_cache', 'tests_framework', 'TemplateMicroservices'}

    for root, dirs, files in os.walk(base_dir):
        # Excluir carpetas ignoradas para no recorrerlas y hacer la búsqueda instantánea
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        if ".env" in files:
            # Es un posible microservicio
            name = os.path.basename(root)
            # Ignorar el propio root del repo si tiene .env general
            if name == os.path.basename(base_dir):
                continue
                
            desc = "No description found."
            try:
                with open(os.path.join(root, ".env"), "r") as f:
                    for line in f:
                        if line.startswith("# DESCRIPCION:"):
                            desc = line.split(":", 1)[1].strip()
                            break
                        elif line.startswith("DESCRIPTION="):
                            desc = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
                        elif line.startswith("APP_DESCRIPTION="):
                            desc = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            except:
                pass
            
            # Formatear la ruta relativa para mostrar mejor la anidación
            rel_path = os.path.relpath(root, base_dir)
            projects.append((rel_path, desc))
                
    if projects:
        print(f"\n {WHITE_NEON}MICROSERVICIOS LOCALIZADOS:{RESET}")
        for idx, (name, desc) in enumerate(projects, 1):
            print(f" {GRAY_NEON}0{idx} ///{RESET} {WHITE_NEON}{name}{RESET}")
            print(f"        {LIGHT_GRAY}{desc}{RESET}\n")
    else:
        print(f"\n {BOLD}No se detectaron microservicios en el root local.{RESET}")

def cmd_go():
    print(f"\n{WHITE_NEON}:: TELETRANSPORTE A MICROSERVICIOS ::{RESET}")
    print(f"{GRAY_NEON}Selecciona tu destino para saltar (cd):{RESET}\n")
    
    projects = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ignore_dirs = {'.git', 'vendor', 'venv', 'node_modules', '__pycache__', '.pytest_cache', 'tests_framework', 'TemplateMicroservices'}

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        if ".env" in files:
            name = os.path.basename(root)
            if name == os.path.basename(base_dir): continue
            rel_path = os.path.relpath(root, base_dir)
            projects.append(rel_path)
            
    if not projects:
        print(f"{WHITE_NEON}[X]{RESET} No se detectaron microservicios.")
        return

    for idx, name in enumerate(projects, 1):
        print(f" {GRAY_NEON}0{idx} ///{RESET} {WHITE_NEON}{name}{RESET}")
        
    try:
        ans = input(f"\n{WHITE_NEON}> {RESET}").strip()
        idx = int(ans) - 1
        if 0 <= idx < len(projects):
            path = os.path.join(base_dir, projects[idx])
            with open("/tmp/.cometax_cd", "w") as f:
                f.write(path)
            print(f"{GRAY_NEON}Teletransportando...{RESET}")
        else:
            print(f"{WHITE_NEON}[X]{RESET} Selección inválida.")
    except Exception:
        sys.exit(0)

def resolve_target(project_name=None):
    if project_name:
        path = get_project_dir_by_name(project_name)
        if path:
            return path
        print(f"{WHITE_NEON}[X]{RESET} Proyecto '{project_name}' no encontrado.")
        sys.exit(1)
    return get_target_directory()

def cmd_run(project_name=None):
    target_dir = resolve_target(project_name)
    env_type, _ = detect_venv_pip(target_dir)
    print(f"\n{GRAY_NEON}>_ LEVANTANDO SERVICIOS: {os.path.basename(target_dir)}{RESET}")
    
    try:
        if env_type == "laravel":
            sail_path = os.path.join(".", "vendor", "bin", "sail")
            if not os.path.exists(os.path.join(target_dir, "vendor", "bin", "sail")):
                print(f"{WHITE_NEON}[X]{RESET} Sail no encontrado. ¿Ejecutaste 'cometax install' o 'composer install'?")
                return
            subprocess.run([sail_path, "up", "-d"], cwd=target_dir)
        else:
            if not os.path.exists(os.path.join(target_dir, "docker-compose.yml")):
                print(f"{WHITE_NEON}[X]{RESET} docker-compose.yml no encontrado.")
                return
            subprocess.run(["docker-compose", "up", "-d", "--build"], cwd=target_dir)
        print(f"{WHITE_NEON}[+]{RESET} Contenedores levantados en segundo plano.")
    except Exception as e:
        print(f"{WHITE_NEON}[X]{RESET} Error ejecutando run: {e}")

def cmd_down(project_name=None):
    target_dir = resolve_target(project_name)
    env_type, _ = detect_venv_pip(target_dir)
    print(f"\n{GRAY_NEON}>_ DETENIENDO SERVICIOS: {os.path.basename(target_dir)}{RESET}")
    
    try:
        if env_type == "laravel":
            sail_path = os.path.join(".", "vendor", "bin", "sail")
            subprocess.run([sail_path, "down"], cwd=target_dir)
        else:
            subprocess.run(["docker-compose", "down"], cwd=target_dir)
        print(f"{WHITE_NEON}[+]{RESET} Contenedores detenidos exitosamente.")
    except Exception as e:
        print(f"{WHITE_NEON}[X]{RESET} Error ejecutando down: {e}")

def cmd_shell(project_name=None):
    target_dir = resolve_target(project_name)
    env_type, _ = detect_venv_pip(target_dir)
    print(f"\n{GRAY_NEON}>_ ENTRANDO AL SHELL: {os.path.basename(target_dir)}{RESET}")
    
    try:
        if env_type == "laravel":
            sail_path = os.path.join(".", "vendor", "bin", "sail")
            subprocess.run([sail_path, "shell"], cwd=target_dir)
        else:
            # En python asumimos que el contenedor principal se llama igual que el dir.
            # O inspeccionamos compose si es necesario. Generalmente 'main' o 'api' o el nombre del proyecto.
            # Haremos un atajo genérico con docker exec o run.sh si existe.
            if os.path.exists(os.path.join(target_dir, "run.sh")):
                subprocess.run(["./run.sh"], cwd=target_dir)
            else:
                # Fallback: Entrar usando sh/bash. Asumiremos main.
                print(f"{WHITE_NEON}[+]{RESET} Usando docker-compose exec para entrar al contenedor...")
                subprocess.run(["docker-compose", "exec", "main", "/bin/sh"], cwd=target_dir)
    except Exception as e:
        print(f"{WHITE_NEON}[X]{RESET} Error entrando al shell: {e}")

def cmd_module(module_name=None):
    cwd = get_target_directory()
    env_type, _ = detect_venv_pip(cwd)
    print(f"\n{GRAY_NEON}>_ CREANDO MÓDULO EN: {os.path.basename(cwd)}{RESET}")
    
    if not module_name:
        module_name = input(f"{WHITE_NEON}Nombre del Módulo (PascalCase): {RESET}").strip()
    
    if not module_name:
        print(f"{WHITE_NEON}[X]{RESET} Nombre inválido.")
        return

    try:
        if env_type == "laravel":
            sail_path = os.path.join(".", "vendor", "bin", "sail")
            if os.path.exists(os.path.join(cwd, "vendor", "bin", "sail")):
                subprocess.run([sail_path, "artisan", "make:module", module_name], cwd=cwd)
            else:
                subprocess.run(["php", "artisan", "make:module", module_name], cwd=cwd)
        else:
            print(f"{WHITE_NEON}[X]{RESET} La creación de módulos CLI por ahora es nativa para Laravel. En Python usa la estructura de carpetas.")
    except Exception as e:
        print(f"{WHITE_NEON}[X]{RESET} Error: {e}")

def cmd_sail_proxy(command_args, action_name):
    cwd = get_target_directory()
    env_type, _ = detect_venv_pip(cwd)
    print(f"\\n{GRAY_NEON}>_ {action_name.upper()} EN: {os.path.basename(cwd)}{RESET}")
    
    try:
        if env_type == "laravel":
            sail_path = os.path.join(".", "vendor", "bin", "sail")
            if os.path.exists(os.path.join(cwd, "vendor", "bin", "sail")):
                print(f"{GRAY_NEON}[i] Asegurando que Sail esté activo...{RESET}")
                subprocess.run([sail_path, "up", "-d"], cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run([sail_path] + command_args, cwd=cwd)
            else:
                subprocess.run(["php"] + command_args, cwd=cwd)
        elif env_type == "python":
            if command_args[0] == "artisan" and command_args[1] == "migrate":
                subprocess.run(["alembic", "upgrade", "head"], cwd=cwd)
            elif command_args[0] == "artisan" and command_args[1] == "test":
                subprocess.run(["pytest"], cwd=cwd)
            else:
                print(f"{WHITE_NEON}[X]{RESET} Comando '{action_name}' no soportado automáticamente en Python por ahora.")
    except Exception as e:
        print(f"{WHITE_NEON}[X]{RESET} Error ejecutando {action_name}: {e}")

def cmd_migrate():
    cmd_sail_proxy(["artisan", "migrate"], "Migrando Base de Datos")

def cmd_seed():
    cmd_sail_proxy(["artisan", "db:seed"], "Insertando Semillas (Seeding)")

def cmd_queue():
    cmd_sail_proxy(["artisan", "queue:work"], "Iniciando Worker de Colas")

def cmd_test():
    cmd_sail_proxy(["artisan", "test"], "Ejecutando Pruebas")

def cmd_test_sentry():
    # Disparar un log de error real via Tinker para validar integración
    cmd_sail_proxy(["artisan", "tinker", "--execute", "Log::error('🔥 Prueba de Integración Sentry - CometaX')"], "Enviando Log de Prueba a Sentry")

def project_context_menu(cwd, env_type):
    name = os.path.basename(cwd)
    print(BANNER)
    print(f" {GRAY_NEON}Estás dentro del microservicio:{RESET} {WHITE_NEON}{name}{RESET} ({env_type.upper()})\\n")
    if env_type == "laravel":
        print(" [1] 🟢 Levantar Servicios (run / up)")
        print(" [2] 🔴 Detener Servicios (down)")
        print(" [3] 📦 Crear Nuevo Módulo")
        print(" [4] 🗄️  Ejecutar Migraciones")
        print(" [5] 🔄 Iniciar Cola de Tareas (Queue)")
        print(" [6] 🧪 Ejecutar Tests")
        print(" [7] 🐚 Entrar al Shell del Contenedor")
        print(" [8] ⚙️  Pasar Comando Libre a Artisan")
        print(" [9] 🛡️  Probar Integración Sentry (Log Error)")
    else:
        print(" [1] 🚀 Abrir Menú Interactivo local (run.sh)")
        print(" [2] 🟢 Levantar Servicios (docker-compose up)")
        print(" [3] 🔴 Detener Servicios (docker-compose down)")
        print(" [4] 🗄️  Ejecutar Migraciones (Alembic)")
        print(" [5] 🧪 Ejecutar Tests (Pytest)")
        print(" [6] 🐚 Entrar al Shell del Contenedor")
    print(" [0] ❌ Salir")
    
    try:
        ans = input(f"\\n{WHITE_NEON}> {RESET}").strip()
        if env_type == "laravel":
            if ans == "1": cmd_run()
            elif ans == "2": cmd_down()
            elif ans == "3": cmd_module()
            elif ans == "4": cmd_migrate()
            elif ans == "5": cmd_queue()
            elif ans == "6": cmd_test()
            elif ans == "7": cmd_shell()
            elif ans == "8":
                custom = input(f"{WHITE_NEON}Escribe el comando de artisan (ej: make:job MiJob): {RESET}").strip()
                if custom:
                    cmd_sail_proxy(["artisan"] + custom.split(), f"Ejecutando Artisan {custom}")
            elif ans == "9": cmd_test_sentry()
            elif ans == "0": sys.exit(0)
            else: print("Opción inválida.")
        elif env_type == "python":
            if ans == "1":
                if os.path.exists(os.path.join(cwd, "run.sh")):
                    subprocess.run(["./run.sh"], cwd=cwd)
                else:
                    print(f"{WHITE_NEON}[X]{RESET} No se encontró run.sh en este proyecto.")
            elif ans == "2": cmd_run()
            elif ans == "3": cmd_down()
            elif ans == "4": cmd_migrate()
            elif ans == "5": cmd_test()
            elif ans == "6": cmd_shell()
            elif ans == "0": sys.exit(0)
            else: print("Opción inválida.")
    except Exception:
        sys.exit(0)

def main():
    if len(sys.argv) < 2:
        try:
            cwd = os.getcwd()
        except (PermissionError, FileNotFoundError):
            # Fallback para macOS cuando el directorio actual ha sido eliminado o es restringido
            cwd = os.environ.get('PWD', os.path.abspath('.'))
            print(f"\n⚠️  Aviso: Problema de permisos en el directorio actual. Usando: {cwd}")
        
        # Verificar si parece ser el root de un microservicio
        if os.path.exists(os.path.join(cwd, ".env")) and (os.path.exists(os.path.join(cwd, "artisan")) or os.path.exists(os.path.join(cwd, "main.py")) or os.path.exists(os.path.join(cwd, "run.sh"))):
            env_type, _ = detect_venv_pip(cwd)
            project_context_menu(cwd, env_type)
        else:
            print_help()
        return

    cmd = sys.argv[1].lower()
    if cmd == "new":
        cmd_new()
    elif cmd == "install":
        pkg = sys.argv[2] if len(sys.argv) > 2 else ""
        cmd_install(pkg)
    elif cmd == "freeze":
        cmd_freeze()
    elif cmd == "projects":
        cmd_projects()
    elif cmd == "go":
        cmd_go()
    elif cmd == "run" or cmd == "up":
        pkg = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_run(pkg)
    elif cmd == "down":
        pkg = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_down(pkg)
    elif cmd == "shell":
        pkg = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_shell(pkg)
    elif cmd == "module":
        pkg = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_module(pkg)
    elif cmd == "migrate":
        cmd_migrate()
    elif cmd == "seed":
        cmd_seed()
    elif cmd == "queue":
        cmd_queue()
    elif cmd == "test":
        cmd_test()
    elif cmd == "test:sentry":
        cmd_test_sentry()
    elif cmd == "make:job":
        cmd_sail_proxy(["artisan", "make:job"] + sys.argv[2:], "Creando Job")
    elif cmd == "make:event":
        cmd_sail_proxy(["artisan", "make:event"] + sys.argv[2:], "Creando Evento")
    else:
        # Fallback: Auto-Passthrough a Artisan si estamos en un proyecto Laravel
        try:
            cwd = os.getcwd()
        except (PermissionError, FileNotFoundError):
            cwd = os.environ.get('PWD', os.path.abspath('.'))
        
        if os.path.exists(os.path.join(cwd, "artisan")):
            print(f"\n{GRAY_NEON}>_ DELEGANDO COMANDO DIRECTO A LARAVEL ARTISAN: {cmd}{RESET}")
            sail_path = os.path.join(".", "vendor", "bin", "sail")
            if os.path.exists(sail_path):
                print(f"{GRAY_NEON}[i] Asegurando que Sail esté activo...{RESET}")
                subprocess.run([sail_path, "up", "-d"], cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                args = [sail_path]
            else:
                args = ["php"]
            args.append("artisan")
            args.extend(sys.argv[1:])
            subprocess.run(args, cwd=cwd)
            return

        print(f"\n {BOLD}Unknown command: {cmd}{RESET}")
        print_help()

if __name__ == "__main__":
    main()
