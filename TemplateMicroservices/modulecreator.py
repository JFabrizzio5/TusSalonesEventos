import os

def capitalize_and_clean_folder_name(name):
    """Convierte el nombre de la carpeta a formato PascalCase (ej. 'Pagos De Prueba' -> 'PagosDePrueba').
    Preserva el casing interno si ya está capitalizado (ej. 'ModuloA' -> 'ModuloA').
    """
    def fix_word(w):
        if not w: return ""
        # Si es todo mayúsculas, lo normalizamos
        if w.isupper() and len(w) > 1:
            return w.capitalize()
        # Si no, solo aseguramos que la primera sea Mayúscula
        return w[0].upper() + w[1:]
        
    return "".join(fix_word(word) for word in name.split())

def create_structure(base_folder, module_name, api_version):
    """Crea la estructura de carpetas y archivos para un módulo específico."""
    module_name_cleaned = capitalize_and_clean_folder_name(module_name)
    module_name_lower = module_name_cleaned.lower()
    module_path = os.path.join(base_folder, module_name_cleaned)
    
    # Verificar si el módulo ya existe
    if os.path.exists(module_path):
        return False
    
    # Crear la carpeta principal del módulo
    os.makedirs(module_path)
    
    # Crear subcarpetas (Incluyendo la carpeta de la VERSIÓN dentro de api)
    subfolders = [
        "api", 
        f"api/{api_version}", # Aquí nace el versionamiento (ej. api/v1)
        "models", 
        "repositories", 
        "services", 
        "validations", 
        "exports", 
        "utils"
    ]
    
    for subfolder in subfolders:
        subfolder_path = os.path.join(module_path, subfolder)
        os.makedirs(subfolder_path, exist_ok=True)
        
        # Crear __init__.py en cada subcarpeta
        init_file = os.path.join(subfolder_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                # Imports relativos dinámicos basados en el nombre del módulo
                if subfolder == "validations":
                    f.write(f"from .{module_name_lower}_validation import validate_{module_name_lower}_data\n")
                elif subfolder == "repositories":
                    f.write(f"from .{module_name_lower}_repository import create_{module_name_lower}\n")
                elif subfolder == "services":
                    f.write(f"from .{module_name_lower}_service import process_create_{module_name_lower}\n")
                elif subfolder == "models":
                    f.write(f"from .{module_name_lower}_models import {module_name_cleaned}CreateRequest, {module_name_cleaned}Response\n")

    # Crear el archivo __init__.py en la raíz del módulo
    with open(os.path.join(module_path, "__init__.py"), "w") as f:
        pass
    
    # Crear los archivos de ejemplo dinámicos
    create_example_files(module_path, module_name_cleaned, module_name_lower, api_version)

    return True

def create_example_files(module_path, module_name, module_lower, api_version):
    """Crea los archivos con el código base usando el nombre dinámico del módulo y la versión."""
    
    # 1. RUTAS (Versionadas en api/v1/routes.py)
    api_folder = os.path.join(module_path, "api", api_version)
    with open(os.path.join(api_folder, "routes.py"), "w") as f:
        f.write(f"""# Ruta: {module_name}/api/{api_version}/routes.py

from fastapi import APIRouter
from {module_name}.models.{module_lower}_models import {module_name}CreateRequest
from {module_name}.services.{module_lower}_service import process_create_{module_lower}
from {module_name}.validations.{module_lower}_validation import validate_{module_lower}_data

router = APIRouter()

@router.post("/create")
async def create_{module_lower}_endpoint(data: {module_name}CreateRequest):
    # 1. Validar
    await validate_{module_lower}_data(data)
    # 2. Procesar en el servicio
    result = await process_create_{module_lower}(data)
    return result    

@router.get("/ping")
async def ping_{module_lower}():
    return {{"message": "{module_name} API {api_version} funcionando correctamente!"}}
""")

    # 2. REPOSITORIOS
    repositories_folder = os.path.join(module_path, "repositories")
    with open(os.path.join(repositories_folder, f"{module_lower}_repository.py"), "w") as f:
        f.write(f"""# Ruta: {module_name}/repositories/{module_lower}_repository.py

from {module_name}.models.{module_lower}_models import {module_name}CreateRequest
# from config import get_database, logger  # Descomentar cuando tengas tu config lista

async def create_{module_lower}(data: {module_name}CreateRequest):
    # Aquí va la lógica de base de datos (Ej. MongoDB o PostgreSQL)
    # collection = await get_database().get_collection("{module_lower}s")
    # result = await collection.insert_one(data.dict())
    # return str(result.inserted_id)
    print("Guardando en base de datos...")
    return "id_ficticio_123"
""")

    # 3. SERVICIOS
    services_folder = os.path.join(module_path, "services")
    with open(os.path.join(services_folder, f"{module_lower}_service.py"), "w") as f:
        f.write(f"""# Ruta: {module_name}/services/{module_lower}_service.py

from {module_name}.repositories.{module_lower}_repository import create_{module_lower}
from {module_name}.models.{module_lower}_models import {module_name}CreateRequest

async def process_create_{module_lower}(data: {module_name}CreateRequest):
    # Aquí va la lógica de negocio antes de guardar
    inserted_id = await create_{module_lower}(data)
    return {{"id": inserted_id, "status": "success"}}
""")

    # 4. VALIDACIONES
    validations_folder = os.path.join(module_path, "validations")
    with open(os.path.join(validations_folder, f"{module_lower}_validation.py"), "w") as f:
        f.write(f"""# Ruta: {module_name}/validations/{module_lower}_validation.py

from fastapi import HTTPException
from {module_name}.models.{module_lower}_models import {module_name}CreateRequest

async def validate_{module_lower}_data(data: {module_name}CreateRequest):
    # Aquí validas reglas de negocio específicas
    if not data.name:
        raise HTTPException(status_code=400, detail="El campo 'name' es requerido")
    return data
""")

    # 5. MODELOS (Pydantic)
    models_folder = os.path.join(module_path, "models")
    with open(os.path.join(models_folder, f"{module_lower}_models.py"), "w") as f:
        f.write(f"""# Ruta: {module_name}/models/{module_lower}_models.py

from pydantic import BaseModel

class {module_name}CreateRequest(BaseModel):
    name: str
    description: str = None

class {module_name}Response(BaseModel):
    id: str
    name: str
""")

def update_main_py(module_name, api_version):
    """Actualiza el archivo main.py con la importación de las rutas versionadas."""
    main_file_path = "main.py"
    module_name_cleaned = capitalize_and_clean_folder_name(module_name)
    module_name_lower = module_name_cleaned.lower()

    # Si main.py no existe, lo crea con la estructura básica de FastAPI
    if not os.path.exists(main_file_path):
        with open(main_file_path, "w") as f:
            f.write("from fastapi import FastAPI\n\napp = FastAPI(title='SaaS Factory API')\n")

    with open(main_file_path, "a") as f:
        # Reemplazamos los puntos por guiones bajos para que sea una variable válida en Python (ej. v1.1 -> v1_1_router)
        safe_version = api_version.replace('.', '_')
        router_alias = f"{module_name_lower}_{safe_version}_router"
        f.write(f"\n# --- Módulo: {module_name_cleaned} ({api_version}) ---")
        f.write(f"\nfrom {module_name_cleaned}.api.{api_version}.routes import router as {router_alias}")
        f.write(f"\napp.include_router({router_alias}, prefix='/{module_name_lower}/{api_version}', tags=['{module_name_cleaned} {api_version.upper()}'])\n")


def generate_md_documentation(base_folder, module_name, api_version):
    """Genera el archivo README.md con la documentación básica del módulo."""
    module_name_cleaned = capitalize_and_clean_folder_name(module_name)
    module_path = os.path.join(base_folder, module_name_cleaned)
    readme_path = os.path.join(module_path, "README.md")
    
    with open(readme_path, "w") as f:
        f.write(f"# Módulo: {module_name_cleaned}\n\n")
        f.write(f"## Versión Actual de la API: `{api_version}`\n\n")
        f.write(f"Este módulo maneja las funcionalidades relacionadas con **{module_name_cleaned.lower()}**.\n\n")
        f.write(f"## Estructura de Carpetas\n")
        f.write(f"- `api/{api_version}/`: Contiene las rutas y endpoints expuestos (Versionados).\n")
        f.write(f"- `models/`: Esquemas de Pydantic.\n")
        f.write(f"- `repositories/`: Conexión directa con la base de datos.\n")
        f.write(f"- `services/`: Lógica de negocio core.\n")
        f.write(f"- `validations/`: Reglas estrictas antes de procesar datos.\n\n")
        f.write(f"## Rutas Registradas\n")
        f.write(f"1. `POST /{module_name_cleaned.lower()}/{api_version}/create`\n")
        f.write(f"2. `GET /{module_name_cleaned.lower()}/{api_version}/ping`\n")


def append_md_documentation(base_folder, module_name, api_version):
    """Agrega la nueva versión al README.md existente sin borrar lo anterior."""
    module_name_cleaned = capitalize_and_clean_folder_name(module_name)
    readme_path = os.path.join(base_folder, module_name_cleaned, "README.md")
    
    if os.path.exists(readme_path):
        with open(readme_path, "a") as f:
            f.write(f"\n---\n## Nueva Versión de la API: `{api_version}`\n")
            f.write(f"Se ha añadido la versión `{api_version}` para extensiones o cambios menores.\n")
            f.write(f"### Nuevas Rutas Registradas\n")
            f.write(f"1. `GET /{module_name_cleaned.lower()}/{api_version}/status`\n")


def add_version_to_module(base_folder, module_name, api_version):
    """Añade solo una nueva carpeta de versión en la API sin sobreescribir el resto del módulo."""
    module_name_cleaned = capitalize_and_clean_folder_name(module_name)
    module_name_lower = module_name_cleaned.lower()
    module_path = os.path.join(base_folder, module_name_cleaned)
    
    api_folder = os.path.join(module_path, "api", api_version)
    if os.path.exists(api_folder):
        print(f"❌ La versión '{api_version}' ya existe en el módulo '{module_name_cleaned}'.")
        return False
        
    os.makedirs(api_folder, exist_ok=True)
    
    # Archivo __init__.py de la nueva versión
    with open(os.path.join(api_folder, "__init__.py"), "w") as f:
        pass
        
    # Crear rutas de ejemplo reutilizando los modelos y servicios ya existentes de la v1
    with open(os.path.join(api_folder, "routes.py"), "w") as f:
        f.write(f"""# Ruta: {module_name_cleaned}/api/{api_version}/routes.py

from fastapi import APIRouter
# Se importa la lógica base para reusarla o extenderla
from {module_name_cleaned}.models.{module_name_lower}_models import {module_name_cleaned}CreateRequest
from {module_name_cleaned}.services.{module_name_lower}_service import process_create_{module_name_lower}

router = APIRouter()

@router.get("/status")
async def status_extension_{api_version.replace('.', '_')}():
    return {{"message": "{module_name_cleaned} API {api_version} - Endpoint para extensiones funcionando"}}
""")
    return True


def run_docker_compose():
    """Ejecuta los comandos docker-compose (Comentado para evitar errores si no hay docker-compose.yml aún)."""
    # os.system('sudo docker-compose down')
    # os.system('sudo docker-compose up --build -d')
    print("-> [Aviso] Reinicio de Docker omitido. Actívalo en el script si tienes el docker-compose.yml listo.")

def main():
    print("=== 🚀 SaaS Factory: Generador de Módulos FastAPI ===")
    base_folder = "."  
    
    module_name = input("Ingrese el nombre del módulo (ej. Pagos, Usuarios, Suscripciones): ")
    module_name_cleaned = capitalize_and_clean_folder_name(module_name)
    module_path = os.path.join(base_folder, module_name_cleaned)
    
    # Lógica inteligente: Si la carpeta ya existe, pregunta si queremos añadir una versión menor (1.1)
    if os.path.exists(module_path):
        print(f"\n[INFO] El módulo '{module_name_cleaned}' ya existe en tu arquitectura.")
        add_version = input("¿Deseas agregar una nueva versión (ej. v1.1) para extensiones o cambios menores? (s/n): ")
        if add_version.lower() == 's':
            api_version = input("Ingrese la nueva versión (ej. v1.1): ") or "v1.1"
            if add_version_to_module(base_folder, module_name, api_version):
                update_main_py(module_name, api_version)
                append_md_documentation(base_folder, module_name, api_version)
                print(f"✅ Versión de extensión '{api_version}' agregada al módulo '{module_name_cleaned}' con éxito.")
            else:
                return
        else:
            print("Operación cancelada.")
            return
    else:
        # Flujo normal para módulos completamente nuevos
        api_version = input("Ingrese la versión inicial de la API [Por defecto: v1]: ") or "v1"
        if create_structure(base_folder, module_name, api_version):
            update_main_py(module_name, api_version)
            generate_md_documentation(base_folder, module_name, api_version)
            print(f"✅ Estructura completa para el módulo '{module_name_cleaned}' ({api_version}) creada con éxito.")
        else:
            return

    print("🔄 Reiniciando servicios...")
    run_docker_compose()
    print("✨ Proceso finalizado. ¡Listo para que tu Junior empiece a programar!")

if __name__ == "__main__":
    main()