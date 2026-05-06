<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
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
                return "<?php\n\nnamespace App\Http\Controllers\\$moduleName;\n\nuse App\Http\Controllers\Controller;\n\nclass {$moduleName}Controller extends Controller\n{\n    public function index()\n    {\n        return response()->json('Welcome to $moduleName');\n    }\n}";
            case 'Models':
                return "<?php\n\nnamespace App\Models\\$moduleName;\n\nuse Illuminate\Database\Eloquent\Model;\n\nclass $moduleName extends Model\n{\n    protected \$table = '" . strtolower($moduleName) . "';\n}";
            case 'Repositories':
                return "<?php\n\nnamespace App\Repositories\\$moduleName;\n\nclass {$moduleName}Repository\n{\n    public function all()\n    {\n        return [];\n    }\n}";
            case 'Services':
                return "<?php\n\nnamespace App\Services\\$moduleName;\n\nuse App\Repositories\\$moduleName\\{$moduleName}Repository;\n\nclass {$moduleName}Service\n{\n    protected \$repository;\n\n    public function __construct({$moduleName}Repository \$repository)\n    {\n        \$this->repository = \$repository;\n    }\n\n    public function getAll()\n    {\n        return \$this->repository->all();\n    }\n}";
            case 'Requests':
                return "<?php\n\nnamespace App\Http\Requests\\$moduleName;\n\nuse Illuminate\Foundation\Http\FormRequest;\n\nclass {$moduleName}Validations extends FormRequest\n{\n    public function authorize()\n    {\n        return true;\n    }\n\n    public function rules()\n    {\n        return [\n            'rfc' => 'required|string|max:13',\n            'password' => 'required|string|min:8',\n        ];\n    }\n\n    public function messages()\n    {\n        return [\n            'rfc.required' => 'El RFC es obligatorio.',\n            'password.required' => 'La contraseña es obligatoria.',\n        ];\n    }\n}";
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
            $importStatement = "\nrequire __DIR__ . '/" . $moduleName . "/api.php';";
            $currentContent = File::get($apiMainPath);
            
            if (!str_contains($currentContent, $importStatement)) {
                File::append($apiMainPath, $importStatement);
                $this->info("Rutas del módulo '$moduleName' vinculadas en routes/api.php");
            }
        }
    }

    private function generateRouteStub($moduleName)
    {
        return "<?php\n\nuse Illuminate\Support\Facades\Route;\nuse App\Http\Controllers\\$moduleName\\{$moduleName}Controller;\n\nRoute::prefix('" . strtolower($moduleName) . "')->group(function () {\n    Route::get('/', [{$moduleName}Controller::class, 'index']);\n});";
    }
}
