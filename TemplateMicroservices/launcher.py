import os
import sys
import re
import time
import shutil
import subprocess
import requests
from factory.envs import create_env_files, create_gitignore
from factory.core import create_core_rt
from factory.db import create_database_config, create_redis_config
from factory.infra import create_docker_compose, create_alembic_setup
from factory.app import create_main_py, create_worker_py, create_requirements, create_dockerfile
from factory.monitoring import create_monitoring_config
from factory.cli import create_commands_py, create_run_sh
from factory.todo import create_todo_module

DB_CHOICES = {
    "1": ("SQL", "sql"),
    "2": ("NoSQL", "mongo"),
    "3": ("Ambos", "both"),
    "4": ("Excel", "excel"),
    "5": ("Ninguna", "none"),
}


def parse_database_choice(choice):
    return DB_CHOICES.get(choice, ("Ninguna", "none"))[1]


def register_in_iam(app_name, description=None):
    """Intenta registrar el microservicio en el IAM para obtener puerto y llave."""
    iam_url = "http://localhost:8000/projects/v1/register"
    try:
        print(f"📡 Registrando '{app_name}' en IAM Control Plane...")
        payload = {"app_name": app_name, "description": description}
        response = requests.post(iam_url, json=payload, timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registro exitoso. Puerto Base: {data['base_port']}, Key: {data['project_key'][:8]}...")
            return data['base_port'], data['project_key'], data['id'], data.get('docker_config', {})
    except Exception as e:
        print(f"⚠️ No se pudo conectar con IAM ({e}). Usando configuración local por defecto.")
    return 8010, "REPLACE_WITH_KEY_FROM_IAM", None, {}

def main():
    WHITE_NEON = "\033[1;97m"
    GRAY_NEON = "\033[1;30m"
    RESET = "\033[0m"

    print(f"{GRAY_NEON}=================================================={RESET}")
    print(f"{WHITE_NEON} 🚀 CometaX Microservices Framework - Modular Architecture {RESET}")
    print(f"{GRAY_NEON}=================================================={RESET}")
    
    name = input(f"{WHITE_NEON}1. Nombre del Microservicio (PascalCase recomendado): {RESET}").strip().replace(" ", "")
    if not name or os.path.exists(name):
        print(f"❌ Error: El nombre '{name}' no es válido o ya existe.")
        return

    description = input("2. Descripción del Proyecto: ").strip()

    print(f"\n{WHITE_NEON}3. Selecciona Framework Interno:{RESET}")
    print(" [1] FastAPI (Python)")
    print(" [2] Laravel 13 (PHP + Sail)")
    framework_choice = input(f"{WHITE_NEON} Elige: {RESET}").strip()
    is_laravel = framework_choice == "2"

    print(f"\n{WHITE_NEON}4. Selecciona Base de Datos:{RESET}")
    for key, (label, _) in DB_CHOICES.items():
        print(f" [{key}] {label}")
    choice = input(f"{WHITE_NEON} Elige: {RESET}").strip()
    db_type = parse_database_choice(choice)

    print(f"\n{WHITE_NEON}5. ¿Deseas integrarlo al IAM Control Plane?{RESET}")
    print(" [1] Sí")
    print(" [2] No (Independiente)")
    iam_choice = input(f"{WHITE_NEON} Elige: {RESET}").strip()
    use_iam = iam_choice == "1"

    # 0. Registro en IAM
    if use_iam:
        base_port, project_key, project_id, docker_config = register_in_iam(name, description)
    else:
        base_port, project_key, project_id, docker_config = 8010, "", None, {}

    if is_laravel:
        # Verificar que Docker esté ejecutándose antes de invocar a laravel.build
        try:
            subprocess.run(["docker", "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            print(f"\n{WHITE_NEON}❌ [ERROR] Docker no está en ejecución.{RESET}")
            print(f"La construcción de Laravel con Laravel Sail requiere que Docker esté activo.")
            print(f"👉 Por favor, abre Docker y vuelve a intentarlo.")
            return

        print(f"\n{WHITE_NEON}📦 Construyendo '{name}' con Laravel 13 y Sail (vía Docker)...{RESET}")
        try:
            # Construir vía laravel.build usando el nombre del proyecto dado (y pedir pgsql/redis si lo requieren, aunque por default trae mysql/pgsql/redis)
            # Laravel.build requiere docker ejecutándose en el equipo del usuario
            # Aplicamos un parche temporal con sed ("s/php85/php84/g") porque la imagen laravelsail/php85-composer aún no existe en DockerHub, rompiendo la instalación.
            subprocess.run(
                f'curl -s "https://laravel.build/{name}?with=pgsql,redis" | sed "s/php85/php84/g" | bash',
                shell=True,
                check=True
            )
            
            if not os.path.exists(os.path.join(name, "artisan")):
                print(f"\\n{WHITE_NEON}❌ [ERROR] Falló la instalación de Laravel.{RESET}")
                print("El contenedor de instalación parece haber fallado en segundo plano (posiblemente falta de red, permisos de volumen de Docker, o cancelación).")
                return

            print(f"{WHITE_NEON}✅ Laravel 13 descargado exitosamente.{RESET}")

            # Instalar Sentry y Scramble (Zero-config OpenAPI) por defecto
            try:
                print(f"📦 Instalando dependencias básicas (Sentry, JWT)...")
                # Paso 1: Dependencias estándar
                subprocess.run(
                    f'docker run --rm -u "$(id -u):$(id -g)" -v "$(pwd)/{name}":/opt -w /opt laravelsail/php84-composer:latest composer require sentry/sentry-laravel firebase/php-jwt -n',
                    shell=True, check=True, stdout=subprocess.DEVNULL
                )
                
                print(f"📦 Instalando Scramble (Docs/OpenAPI)...")
                # Paso 2: Scramble por separado para evitar conflictos de auto-discovery
                subprocess.run(
                    f'docker run --rm -u "$(id -u):$(id -g)" -v "$(pwd)/{name}":/opt -w /opt laravelsail/php84-composer:latest composer require dedoc/scramble -n',
                    shell=True, check=True, stdout=subprocess.DEVNULL
                )

                print(f"⚙️  Configurando API y Sentry...")
                # Paso 3: Publicar Sentry y configurar API
                deps_cmd = (
                    f'docker run --rm -u "$(id -u):$(id -g)" -v "$(pwd)/{name}":/opt -w /opt '
                    f'laravelsail/php84-composer:latest bash -c '
                    f'"(php artisan install:api -n || true) '
                    f'&& php artisan vendor:publish --provider=Sentry\\\\Laravel\\\\ServiceProvider --force"'
                )
                subprocess.run(deps_cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
            except Exception as e:
                print(f"\\n⚠️  Aviso: Algunas dependencias extra fallaron o ya estaban: {e}")

            # Inyectar Endpoints de Prueba en Laravel
            api_routes_path = os.path.join(name, "routes", "api.php")
            if os.path.exists(api_routes_path):
                # Remover la ruta '/user' por defecto para evitar que Scramble tire errores de DB
                with open(api_routes_path, "r") as f:
                    api_content = f.read()
                
                # Usar regex o reemplazo para quitar el bloque de Sanctum (Evita errores de DB iniciales)
                api_content = re.sub(r"Route::get\('/user'.*?\}\)->middleware\('auth:sanctum'\);", "", api_content, flags=re.DOTALL)
                
                with open(api_routes_path, "w") as f:
                    f.write(api_content)
                    f.write("\n\n// --- CometaX Default Tools ---\n")
                    f.write("Route::get('/health', function () {\n")
                    f.write("    return response()->json(['status' => 'ok', 'app' => env('APP_NAME')]);\n")
                    f.write("});\n\n")
                    f.write("// --- Diagnóstico Sentry Full-Stack (CometaX Diagnostics) ---\n")
                    f.write("use Illuminate\\Support\\Facades\\Log;\n")
                    f.write("use Illuminate\\Support\\Facades\\DB;\n\n")
                    f.write("Route::get('/test-sentry', function () {\n")
                    f.write("    // 0. Forzar nombre de transacción para Discover y Metrics\n")
                    f.write("    \\Sentry\\SentrySdk::getCurrentHub()->getTransaction()?->setName('cometax.diagnostic.full_suite');\n\n")
                    f.write("    // 1. Identidad de Usuario (Aparecerá en Discover > User)\n")
                    f.write("    \\Sentry\\configureScope(function (\\Sentry\\State\\Scope $scope): void {\n")
                    f.write(f"        $scope->setUser(['id' => 777, 'email' => '{name}-diagnostic@cometax.com', 'username' => '{name}Master']);\n")
                    f.write("        $scope->setTag('cometax_diagnostic', 'true');\n")
                    f.write("    });\n\n")
                    f.write("    // 2. Métrica de inicio de diagnóstico\n")
                    f.write("    \\Sentry\\traceMetrics()->count('cometax.diagnostic.start', 1);\n\n")
                    f.write("    // 3. Breadcrumb: Paso previo a DB\n")
                    f.write("    \\Sentry\\addBreadcrumb(new \\Sentry\\Breadcrumb(\\Sentry\\Breadcrumb::LEVEL_INFO, \\Sentry\\Breadcrumb::TYPE_DEFAULT, 'db', 'Intentando conectar a DB para validar drivers...'));\n\n")
                    f.write("    // 4. Trace de Conexión a Base de Datos (Esto capturará errores de Driver)\n")
                    f.write("    try {\n")
                    f.write("        \\Illuminate\\Support\\Facades\\DB::connection()->getPdo();\n")
                    f.write("        \\Sentry\\addBreadcrumb(new \\Sentry\\Breadcrumb(\\Sentry\\Breadcrumb::LEVEL_INFO, \\Sentry\\Breadcrumb::TYPE_DEFAULT, 'db', 'Conexión a DB exitosa.'));\n")
                    f.write("    } catch (\\Exception $e) {\n")
                    f.write(f"        \\Illuminate\\Support\\Facades\\Log::error('Fallo de conectividad detectado en {name}: ' . $e->getMessage());\n")
                    f.write("    }\n\n")
                    f.write("    // 5. El Gran Final con Excepción Completa\n")
                    f.write("    \\Sentry\\flush(); // <--- CRÍTICO: Asegura que las métricas y logs se envíen antes de que Laravel mate el proceso\n")
                    f.write(f"    throw new \\Exception('🔥 Diagnóstico Discover en {name}: Si ves esto, cambia el filtro de proyecto en Sentry a \"All Projects\".');\n")
                    f.write("});\n")

            # Escribir el comando custom CreateModule.php
            cmd_path = os.path.join(name, "app", "Console", "Commands")
            os.makedirs(cmd_path, exist_ok=True)
            create_module_content = """<?php

namespace App\\Console\\Commands;

use Illuminate\\Console\\Command;
use File;

class CreateModule extends Command
{
    protected $signature = 'make:module {name}';
    protected $description = 'Crea un módulo con controlador, modelo, repositorio, validación y archivo de rutas';

    public function __construct()
    {
        parent::__construct();
    }

    public function handle()
    {
        $moduleName = $this->argument('name');

        // Crear subcarpetas dentro de las carpetas principales
        $basePaths = [
            'Controllers' => app_path('Http/Controllers'),
            'Models' => app_path('Models'),
            'Repositories' => app_path('Repositories'),
            'Services' => app_path('Services'),
            'Requests' => app_path('Http/Requests'), // Carpeta de validaciones
        ];

        foreach ($basePaths as $key => $path) {
            $modulePath = $path . '/' . $moduleName;
            if (!File::exists($modulePath)) {
                File::makeDirectory($modulePath, 0777, true);
                $this->info("Directorio creado: $modulePath");
            }

            // Crear archivo correspondiente dentro de cada carpeta
            $stub = $this->generateStub($key, $moduleName);
            $fileName = $moduleName . ($key === 'Controllers' ? 'Controller' : ($key === 'Requests' ? 'Validations' : ($key === 'Services' ? 'Service' : ''))) . '.php';
            File::put("$modulePath/$fileName", $stub);
            $this->info("Archivo creado: $modulePath/$fileName");
        }

        // Crear archivo de rutas
        $this->createRoutes($moduleName);

        $this->info("Módulo '$moduleName' creado correctamente.");
    }

    private function generateStub($type, $moduleName)
    {
        switch ($type) {
            case 'Controllers':
                return "<?php\\n\\nnamespace App\\\\Http\\\\Controllers\\\\$moduleName;\\n\\nuse App\\\\Http\\\\Controllers\\\\Controller;\\n\\nclass {$moduleName}Controller extends Controller\\n{\\n    public function index()\\n    {\\n        return response()->json('Welcome to $moduleName');\\n    }\\n}";
            case 'Models':
                return "<?php\\n\\nnamespace App\\\\Models\\\\$moduleName;\\n\\nuse Illuminate\\\\Database\\\\Eloquent\\\\Model;\\n\\nclass $moduleName extends Model\\n{\\n    protected \\$table = '" . strtolower($moduleName) . "';\\n}";
            case 'Repositories':
                return "<?php\\n\\nnamespace App\\\\Repositories\\\\$moduleName;\\n\\nclass {$moduleName}Repository\\n{\\n    public function all()\\n    {\\n        return [];\\n    }\\n}";
            case 'Services':
                return "<?php\\n\\nnamespace App\\\\Services\\\\$moduleName;\\n\\nuse App\\\\Repositories\\\\$moduleName\\\\{$moduleName}Repository;\\n\\nclass {$moduleName}Service\\n{\\n    protected \\$repository;\\n\\n    public function __construct({$moduleName}Repository \\$repository)\\n    {\\n        \\$this->repository = \\$repository;\\n    }\\n\\n    public function getAll()\\n    {\\n        return \\$this->repository->all();\\n    }\\n}";
            case 'Requests':
                return "<?php\\n\\nnamespace App\\\\Http\\\\Requests\\\\$moduleName;\\n\\nuse Illuminate\\\\Foundation\\\\Http\\\\FormRequest;\\n\\nclass {$moduleName}Validations extends FormRequest\\n{\\n    public function authorize()\\n    {\\n        return true;\\n    }\\n\\n    public function rules()\\n    {\\n        return [\\n            'rfc' => 'required|string|max:13',\\n            'password' => 'required|string|min:8',\\n        ];\\n    }\\n\\n    public function messages()\\n    {\\n        return [\\n            'rfc.required' => 'El RFC es obligatorio.',\\n            'password.required' => 'La contraseña es obligatoria.',\\n        ];\\n    }\\n}";
        }
    }

    private function createRoutes($moduleName)
    {
        $routesPath = base_path('routes/' . $moduleName);
        if (!File::exists($routesPath)) {
            File::makeDirectory($routesPath, 0777, true);
            $this->info("Directorio de rutas creado: $routesPath");
        }

        $routeFileName = "api.php";
        $routeStub = $this->generateRouteStub($moduleName);
        File::put("$routesPath/$routeFileName", $routeStub);
        $this->info("Archivo de rutas creado: $routesPath/$routeFileName");

        // --- Registro Automático en routes/api.php ---
        $apiMainPath = base_path('routes/api.php');
        if (File::exists($apiMainPath)) {
            $importStatement = "\\nrequire __DIR__ . '/" . $moduleName . "/api.php';";
            $currentContent = File::get($apiMainPath);
            
            if (!str_contains($currentContent, $importStatement)) {
                File::append($apiMainPath, $importStatement);
                $this->info("Rutas del módulo '$moduleName' vinculadas en routes/api.php");
            }
        }
    }

    private function generateRouteStub($moduleName)
    {
        return "<?php\\n\\nuse Illuminate\\\\Support\\\\Facades\\\\Route;\\nuse App\\\\Http\\\\Controllers\\\\$moduleName\\\\{$moduleName}Controller;\\n\\nRoute::prefix('" . strtolower($moduleName) . "')->group(function () {\\n    Route::get('/', [{$moduleName}Controller::class, 'index']);\\n});";
    }
}
"""
            with open(os.path.join(cmd_path, "CreateModule.php"), "w") as f:
                f.write(create_module_content)

            # --- NUEVO: Inyectar Middleware de IAM (CometaX Standard) ---
            if use_iam:
                print(f"🛡️  Inyectando Seguridad CometaX (IAM Middleware)...")
                middleware_path = os.path.join(name, "app", "Http", "Middleware")
                os.makedirs(middleware_path, exist_ok=True)
                iam_middleware_content = """<?php

namespace App\\Http\\Middleware;

use Closure;
use Illuminate\\Http\\Request;
use Illuminate\\Support\\Facades\\Http;
use Illuminate\\Support\\Facades\\Log;
use Illuminate\\Support\\Facades\\Cache;
use Firebase\\JWT\\JWT;
use Firebase\\JWT\\JWK;

class CometaxIamMiddleware
{
    /**
     * Middleware de Seguridad CometaX para validación distribuida de IAM (RS256).
     */
    public function handle(Request $request, Closure $next)
    {
        // 1. Rutas públicas exceptuadas
        if ($request->is('health', 'metrics', 'docs', 'openapi.json', 'up', 'test-sentry')) {
            return $next($request);
        }

        $iamUrl = env('IAM_URL', 'http://localhost:8000');
        $requireAuth = env('REQUIRE_AUTH', false);
        $expectedInternalKey = env('INTERNAL_APP_KEY');

        // 2. Validación de Llamada Interna (M2M)
        $internalKey = $request->header('X-Internal-Key');
        if ($internalKey && $expectedInternalKey) {
            if ($internalKey === $expectedInternalKey) {
                $request->attributes->set('tenant_id', $request->header('X-Tenant-ID'));
                $request->attributes->set('user_id', 'internal-service');
                $request->attributes->set('is_internal', true);
                return $next($request);
            }
            return response()->json(['detail' => 'Credencial interna inválida'], 401);
        }

        // 3. Validación de Usuario vía JWT (RS256)
        $authHeader = $request->header('Authorization');
        if ($authHeader && str_starts_with($authHeader, 'Bearer ')) {
            $token = substr($authHeader, 7);
            try {
                // Obtener JWKS (Llaves Públicas) del IAM con Caché
                $jwks = Cache::remember('cometax_jwks', 300, function () use ($iamUrl) {
                    $response = Http::get("{$iamUrl}/.well-known/jwks.json");
                    return $response->successful() ? $response->json() : null;
                });

                if (!$jwks) {
                    return response()->json(['detail' => 'No se pudo obtener la llave pública de validación del IAM'], 401);
                }

                // Decodificar usando el set de llaves (maneja automáticamente kids)
                $keys = JWK::parseKeySet($jwks);
                $decoded = JWT::decode($token, $keys);
                
                $tenantId = $decoded->tenant_id ?? null;

                // 4. Validación de Proyecto/Tenant Activo
                if ($tenantId) {
                    $isProjectActive = Cache::remember("iam_tenant_valid:{$tenantId}", 60, function () use ($iamUrl, $tenantId) {
                        return Http::get("{$iamUrl}/projects/v1/validate/{$tenantId}")->successful();
                    });

                    if (!$isProjectActive) {
                        return response()->json(['detail' => 'Proyecto o Tenant inactivo/no autorizado'], 403);
                    }
                }

                // Inyectar contexto en el request
                $request->attributes->set('tenant_id', $tenantId);
                $request->attributes->set('user_id', $decoded->sub ?? null);
                $request->attributes->set('is_internal', false);
                $request->attributes->set('iam_payload', (array)$decoded);

            } catch (\\Exception $e) {
                Log::error("❌ [IAM] Error de validación: " . $e->getMessage());
                return response()->json(['detail' => 'Token inválido o expirado'], 401);
            }
        } else {
            if ($requireAuth) {
                return response()->json(['detail' => 'Autenticación requerida'], 401);
            }
        }

        return $next($request);
    }
}
"""
                with open(os.path.join(middleware_path, "CometaxIamMiddleware.php"), "w") as f:
                    f.write(iam_middleware_content)

                # Registrar el Middleware en bootstrap/app.php (Laravel 11+)
                bootstrap_path = os.path.join(name, "bootstrap", "app.php")
                if os.path.exists(bootstrap_path):
                    with open(bootstrap_path, "r") as f:
                        bt_content = f.read()
                    
                    # Registro de Middleware e Integración Sentry (Laravel 11+)
                    # Asegurar el 'use' de Sentry
                    if "use Sentry\\Laravel\\Integration;" not in bt_content:
                        bt_content = re.sub(
                            r"use Illuminate\\Foundation\\Configuration\\Middleware;",
                            r"use Illuminate\\Foundation\\Configuration\\Middleware;\nuse Sentry\\Laravel\\Integration;",
                            bt_content
                        )

                    # Inyectar Middleware (Prepend Tracing, Append IAM)
                    # Patrón ultra-flexible para detectar el bloque de middleware
                    middleware_pattern = r"->withMiddleware\(function\s*\(\s*Middleware\s*\$middleware\s*\)\s*(?::\s*void)?\s*{\s*(?://)?\s*}\s*\)"
                    middleware_replacement = r"->withMiddleware(function (Middleware $middleware): void {\n        $middleware->prepend(\\Sentry\\Laravel\\Tracing\\Middleware::class);\n        $middleware->append(\\App\\Http\\Middleware\\CometaxIamMiddleware::class);\n    })"
                    
                    # Si ya tiene contenido o comentario diferente
                    if not re.search(middleware_pattern, bt_content):
                         middleware_pattern = r"->withMiddleware\(function\s*\(\s*Middleware\s*\$middleware\s*\)\s*(?::\s*void)?\s*{\s*//\s*}\s*\)"
                    
                    bt_content = re.sub(middleware_pattern, middleware_replacement, bt_content)

                    # Inyectar Exceptions (Integration::handles)
                    exceptions_pattern = r"->withExceptions\(function\s*\(\s*Exceptions\s*\$exceptions\s*\)\s*(?::\s*void)?\s*{\s*(?://)?\s*}\s*\)"
                    exceptions_replacement = r"->withExceptions(function (Exceptions $exceptions): void {\n        Integration::handles($exceptions);\n    })"
                    
                    if not re.search(exceptions_pattern, bt_content):
                        exceptions_pattern = r"->withExceptions\(function\s*\(\s*Exceptions\s*\$exceptions\s*\)\s*(?::\s*void)?\s*{\s*//\s*}\s*\)"
                        
                    bt_content = re.sub(exceptions_pattern, exceptions_replacement, bt_content)
                    
                    with open(bootstrap_path, "w") as f:
                        f.write(bt_content)

                # Inyectar canal Sentry en config/logging.php (Structured Logs v4.15+)
                logging_path = os.path.join(name, "config", "logging.php")
                if os.path.exists(logging_path):
                    with open(logging_path, "r") as f:
                        log_content = f.read()
                    
                    sentry_channel = r"'channels' => [\n        'sentry_logs' => [\n            'driver' => 'sentry_logs',\n        ],"
                    if "'sentry_logs' => [" not in log_content:
                        # Búsqueda elástica del inicio de channels
                        log_content = re.sub(r"'channels'\s*=>\s*\[", sentry_channel, log_content, count=1)
                        with open(logging_path, "w") as f:
                            f.write(log_content)
                
                # Inyectar endpoint de prueba de Sentry en routes/api.php (Diagnóstico Total)
                api_routes_path = os.path.join(name, "routes", "api.php")
                # Ya inyectado durante la creación base, pero aseguramos .env
                
            # Modificar y sobreescribir el .env generado por Laravel
            env_path = os.path.join(name, ".env")
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    env_content = f.read()

                # Cambiar el driver de sesión a file por defecto para evitar QueryException en BD vacía
                env_content = env_content.replace("SESSION_DRIVER=database", "SESSION_DRIVER=file")

                with open(env_path, "w") as f:
                    # Cambiar LOG_STACK por defecto (Structured Logs)
                    env_content = env_content.replace("LOG_STACK=single", "LOG_STACK=single,sentry_logs")
                    f.write(env_content)
                    f.write("\n# --- Traceability & Logs ---\n")
                    f.write("SENTRY_ENABLE_LOGS=true\n")
                    f.write("SENTRY_SEND_DEFAULT_PII=true\n")
                    f.write("SENTRY_ENVIRONMENT=local\n")
                    f.write("SENTRY_LARAVEL_DSN=https://47036b8f72bfdf2c741b2d173838827c@o4511147272568832.ingest.us.sentry.io/4511148836454400\n")
                    f.write("SENTRY_DSN=https://47036b8f72bfdf2c741b2d173838827c@o4511147272568832.ingest.us.sentry.io/4511148836454400\n")
                    f.write("SENTRY_TRACES_SAMPLE_RATE=1.0\n")
                    f.write(f"SENTRY_TAGS=service:{name},version:1.0.0\n")

                if use_iam:
                    with open(env_path, "a") as f:
                        f.write("\n# --- CometaX Microservices Injection ---\n")
                        f.write(f"APP_DESCRIPTION=\"{description}\"\n")
                        f.write(f"IAM_URL=http://localhost:8000\n")
                        f.write(f"PROJECT_KEY={project_key}\n")

            # Documentar en el README.md
            readme_content = f"""# {name}

{description}

Microservicio generado con **CometaX** y **Laravel 13 (Sail)**.

## 🚀 Despliegue con Laravel Sail
Para ejecutar este proyecto, asegúrate de tener Docker abierto.

```bash
cd {name}
./vendor/bin/sail up -d
./vendor/bin/sail artisan migrate
```

## 🏗️ Creación de Módulos (CometaX Standard)
Este proyecto incluye el comando personalizado `make:module` para generar la arquitectura limpia de CometaX automáticamente (Controladores, Modelos, Repositorios, Rutas y Validaciones en carpetas encapsuladas).

Ejecuta el siguiente comando a través de Sail para generar un módulo:
```bash
./vendor/bin/sail artisan make:module NombreDeTuModulo
```
"""
            with open(os.path.join(name, "README.md"), "w") as f:
                f.write(readme_content)

            print(f"\\n{WHITE_NEON}✅ Microservicio '{name}' creado exitosamente bajo Laravel 13.{RESET}")
            print(f"👉 Entra a la carpeta: cd {name}")
            print(f"👉 Inicia el servidor Sail: ./vendor/bin/sail up -d")
            print(f"👉 Prepara la BD: ./vendor/bin/sail artisan migrate")
            print(f"👉 Crea tu primer módulo: ./vendor/bin/sail artisan make:module Ejemplo")
            print(f"👉 Prueba Sentry: http://localhost/api/test-sentry")
            
            print(f"\\n{GRAY_NEON}⚠️  Aviso: Las extensiones como php-redis y ext-mongodb ya vienen incluidas o pueden requerirse según tu stack.{RESET}")
            print(f"{GRAY_NEON}Si usas contenedores Sail todo está cubierto, si ejecutas local vía Composer, visita:{RESET}")
            print(f"{GRAY_NEON}- Redis: https://laravel.com/docs/redis{RESET}")
            print(f"{GRAY_NEON}- MongoDB: https://github.com/mongodb/laravel-mongodb{RESET}")
            print(f"{GRAY_NEON}=================================================={RESET}")
            return
        except Exception as e:
            print(f"❌ Falló la instalación de Laravel: {e}")
            return

    # ==========================================
    # LÓGICA DE PYTHON (FastAPI)
    # ==========================================
    # 1. Crear Estructura Base
    os.makedirs(name)
    os.makedirs(os.path.join(name, "modules"))
    
    # 2. Construcción por Módulos
    print(f"📦 Construyendo '{name}'...")
    
    create_env_files(name, db_type, base_port, description, use_iam=use_iam)
    
    # Inyectar la llave real en los .env
    if use_iam:
        for env_file in [".env", ".env.dev", ".env.prod", ".env.docker"]:
            path = os.path.join(name, env_file)
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read()
                content = content.replace("REPLACE_WITH_KEY_FROM_IAM", project_key)
                with open(path, "w") as f:
                    f.write(content)

    create_gitignore(name)
    create_core_rt(name)
    create_database_config(name, db_type)
    create_redis_config(name)
    create_docker_compose(name, name, db_type, docker_config)
    create_main_py(name, name, use_iam=use_iam)
    create_worker_py(name, name)
    create_requirements(name, db_type)
    create_dockerfile(name)
    create_monitoring_config(name)
    create_commands_py(name)
    create_run_sh(name)
    
    if db_type in ["sql", "both"]:
        create_alembic_setup(name)
    if db_type in ["sql", "both", "excel"]:
        create_todo_module(name, db_type)

    # 3. Automatización de Entorno Local (venv)
    print(f"\\n⚙️  Configurando Entorno Virtual (venv) en './{name}/venv'...")
    try:
        subprocess.run([sys.executable, "-m", "venv", os.path.join(name, "venv")], check=True)
        print("📦 Instalando dependencias en el venv (esto puede tardar unos segundos)...")
        # Acceder al pip del venv generado
        pip_path = os.path.join(name, "venv", "bin", "pip")
        if not os.path.exists(pip_path): # Windows fallback
             pip_path = os.path.join(name, "venv", "Scripts", "pip")
        
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True, capture_output=True)
        subprocess.run([pip_path, "install", "-r", os.path.join(name, "requirements.txt")], check=True, capture_output=True)
        print("✅ Entorno Virtual configurado y listo.")
    except Exception as e:
        print(f"⚠️  Nota: No se pudo auto-configurar el venv: {e}")
        print("👉 Deberás crearlo manualmente: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")

    print(f"\\n✅ Microservicio '{name}' creado exitosamente (FastAPI).")
    print(f"👉 Entra a la carpeta: cd {name}")
    print(f"👉 Inicia el panel: ./run.sh")
    print(f"{GRAY_NEON}=================================================={RESET}")

if __name__ == "__main__":
    main()
