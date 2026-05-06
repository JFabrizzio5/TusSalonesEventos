"""
Test exhaustivo para modulecreator.py
Corre todos los escenarios y reporta resultados.
"""

import os
import sys
import shutil
import importlib.util
import traceback

# ──────────────────────────────────────────────
# Carga dinámica del módulo a testear
# ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MC_PATH = os.path.join(SCRIPT_DIR, "modulecreator.py")

spec = importlib.util.spec_from_file_location("modulecreator", MC_PATH)
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
TEST_BASE = os.path.join(SCRIPT_DIR, "_TEST_PLAYGROUND")
RESULTS = []

def setup():
    os.makedirs(TEST_BASE, exist_ok=True)

def teardown():
    if os.path.exists(TEST_BASE):
        shutil.rmtree(TEST_BASE)

def assert_it(condition, msg):
    if not condition:
        raise AssertionError(msg)

def record(name, passed, detail=""):
    icon = "✅" if passed else "❌"
    RESULTS.append((icon, name, detail))

def run_test(name, fn):
    try:
        fn()
        record(name, True)
    except AssertionError as e:
        record(name, False, str(e))
    except Exception:
        record(name, False, traceback.format_exc().strip().split("\n")[-1])

# ──────────────────────────────────────────────
# TESTS
# ──────────────────────────────────────────────

def test_capitalize_clean():
    assert_it(mc.capitalize_and_clean_folder_name("pagos") == "Pagos", "nombre simple")
    assert_it(mc.capitalize_and_clean_folder_name("  pagos  ") == "Pagos", "con espacios")
    assert_it(mc.capitalize_and_clean_folder_name("Pagos De Prueba") == "PagosDePrueba", "multi-palabra")
    assert_it(mc.capitalize_and_clean_folder_name("USUARIOS") == "Usuarios", "todo mayúsculas")
    assert_it(mc.capitalize_and_clean_folder_name("a") == "A", "un solo carácter")

def test_create_structure_v1():
    """Crea módulo normal con v1"""
    mc.create_structure(TEST_BASE, "Pagos", "v1")
    path = os.path.join(TEST_BASE, "Pagos")
    assert_it(os.path.isdir(path), "carpeta raíz")
    assert_it(os.path.isdir(os.path.join(path, "api", "v1")), "carpeta api/v1")
    assert_it(os.path.isfile(os.path.join(path, "api", "v1", "routes.py")), "routes.py")
    assert_it(os.path.isfile(os.path.join(path, "models", "pagos_models.py")), "models py")
    assert_it(os.path.isfile(os.path.join(path, "services", "pagos_service.py")), "service py")
    assert_it(os.path.isfile(os.path.join(path, "repositories", "pagos_repository.py")), "repo py")
    assert_it(os.path.isfile(os.path.join(path, "validations", "pagos_validation.py")), "validation py")

def test_create_structure_custom_version():
    """Versión personalizada v2"""
    mc.create_structure(TEST_BASE, "Facturas", "v2")
    path = os.path.join(TEST_BASE, "Facturas")
    assert_it(os.path.isdir(os.path.join(path, "api", "v2")), "carpeta api/v2")
    assert_it(os.path.isfile(os.path.join(path, "api", "v2", "routes.py")), "routes.py v2")

def test_create_structure_duplicate_returns_false():
    """No debe sobreescribir módulo existente"""
    mc.create_structure(TEST_BASE, "Suscripciones", "v1")
    result = mc.create_structure(TEST_BASE, "Suscripciones", "v1")
    assert_it(result == False, "debe retornar False si existe")

def test_init_files_content():
    """Verifica contenido de __init__.py en subcarpetas"""
    mc.create_structure(TEST_BASE, "Usuarios", "v1")
    path = os.path.join(TEST_BASE, "Usuarios")

    with open(os.path.join(path, "validations", "__init__.py")) as f:
        content = f.read()
    assert_it("validate_usuarios_data" in content, "init validations import")

    with open(os.path.join(path, "services", "__init__.py")) as f:
        content = f.read()
    assert_it("process_create_usuarios" in content, "init services import")

    with open(os.path.join(path, "repositories", "__init__.py")) as f:
        content = f.read()
    assert_it("create_usuarios" in content, "init repos import")

    with open(os.path.join(path, "models", "__init__.py")) as f:
        content = f.read()
    assert_it("UsuariosCreateRequest" in content, "init models import")

def test_routes_content():
    """Verifica que routes.py tenga los endpoints correctos"""
    mc.create_structure(TEST_BASE, "Notificaciones", "v1")
    routes_path = os.path.join(TEST_BASE, "Notificaciones", "api", "v1", "routes.py")
    with open(routes_path) as f:
        content = f.read()
    assert_it("@router.post(\"/create\")" in content, "endpoint POST /create")
    assert_it("@router.get(\"/ping\")" in content, "endpoint GET /ping")
    assert_it("Notificaciones API v1 funcionando" in content, "mensaje ping")
    assert_it("validate_notificaciones_data" in content, "llama a validación")
    assert_it("process_create_notificaciones" in content, "llama a servicio")

def test_models_content():
    """Verifica estructura Pydantic en models"""
    mc.create_structure(TEST_BASE, "Pedidos", "v1")
    models_path = os.path.join(TEST_BASE, "Pedidos", "models", "pedidos_models.py")
    with open(models_path) as f:
        content = f.read()
    assert_it("class PedidosCreateRequest(BaseModel)" in content, "clase Request")
    assert_it("class PedidosResponse(BaseModel)" in content, "clase Response")
    assert_it("from pydantic import BaseModel" in content, "import pydantic")

def test_validation_content():
    """Valida que validation.py tenga HTTPException y la guarda"""
    mc.create_structure(TEST_BASE, "Inventario", "v1")
    v_path = os.path.join(TEST_BASE, "Inventario", "validations", "inventario_validation.py")
    with open(v_path) as f:
        content = f.read()
    assert_it("from fastapi import HTTPException" in content, "import HTTPException")
    assert_it("raise HTTPException" in content, "lanza excepción")
    assert_it("async def validate_inventario_data" in content, "función async")

def test_add_version_to_existing_module():
    """Agrega versión v1.1 a módulo existente"""
    mc.create_structure(TEST_BASE, "Reportes", "v1")
    result = mc.add_version_to_module(TEST_BASE, "Reportes", "v1.1")
    assert_it(result == True, "debe retornar True")
    new_routes = os.path.join(TEST_BASE, "Reportes", "api", "v1.1", "routes.py")
    assert_it(os.path.isfile(new_routes), "routes.py de v1.1 existe")
    with open(new_routes) as f:
        content = f.read()
    assert_it("@router.get(\"/status\")" in content, "endpoint /status en v1.1")

def test_add_duplicate_version_returns_false():
    """No duplica versión ya existente"""
    mc.create_structure(TEST_BASE, "Clientes", "v1")
    mc.add_version_to_module(TEST_BASE, "Clientes", "v1.1")
    result = mc.add_version_to_module(TEST_BASE, "Clientes", "v1.1")
    assert_it(result == False, "retorna False si versión ya existe")

def test_readme_generated():
    """README.md tiene contenido correcto"""
    mc.create_structure(TEST_BASE, "Documentos", "v1")
    mc.generate_md_documentation(TEST_BASE, "Documentos", "v1")
    readme = os.path.join(TEST_BASE, "Documentos", "README.md")
    assert_it(os.path.isfile(readme), "README.md existe")
    with open(readme) as f:
        content = f.read()
    assert_it("# Módulo: Documentos" in content, "título correcto")
    assert_it("v1" in content, "versión en README")
    assert_it("POST /documentos/v1/create" in content, "ruta POST documentada")
    assert_it("GET /documentos/v1/ping" in content, "ruta GET documentada")

def test_readme_append_new_version():
    """append_md_documentation agrega sin borrar"""
    mc.create_structure(TEST_BASE, "Contratos", "v1")
    mc.generate_md_documentation(TEST_BASE, "Contratos", "v1")
    mc.add_version_to_module(TEST_BASE, "Contratos", "v2")
    mc.append_md_documentation(TEST_BASE, "Contratos", "v2")
    readme = os.path.join(TEST_BASE, "Contratos", "README.md")
    with open(readme) as f:
        content = f.read()
    assert_it("# Módulo: Contratos" in content, "sección v1 sigue")
    assert_it("Nueva Versión de la API: `v2`" in content, "sección v2 añadida")

def test_update_main_py_new():
    """Crea main.py si no existe y agrega router"""
    test_dir = os.path.join(TEST_BASE, "main_test_new")
    os.makedirs(test_dir, exist_ok=True)
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    try:
        mc.create_structure(".", "Envios", "v1")
        mc.update_main_py("Envios", "v1")
        assert_it(os.path.isfile("main.py"), "main.py creado")
        with open("main.py") as f:
            content = f.read()
        assert_it("from fastapi import FastAPI" in content, "import FastAPI")
        assert_it("from Envios.api.v1.routes import router" in content, "router import")
        assert_it("app.include_router" in content, "include_router llamado")
        assert_it("prefix='/envios/v1'" in content, "prefix correcto")
    finally:
        os.chdir(original_cwd)

def test_update_main_py_appends():
    """Agrega segundo router sin borrar el primero"""
    test_dir = os.path.join(TEST_BASE, "main_test_append")
    os.makedirs(test_dir, exist_ok=True)
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    try:
        mc.create_structure(".", "ModuloA", "v1")
        mc.update_main_py("ModuloA", "v1")
        mc.create_structure(".", "ModuloB", "v1")
        mc.update_main_py("ModuloB", "v1")
        with open("main.py") as f:
            content = f.read()
        assert_it("from ModuloA.api.v1.routes import router" in content, "router ModuloA")
        assert_it("from ModuloB.api.v1.routes import router" in content, "router ModuloB")
    finally:
        os.chdir(original_cwd)

def test_multiword_module_name():
    """Módulo con nombre de dos palabras"""
    mc.create_structure(TEST_BASE, "Gestion Riesgos", "v1")
    path = os.path.join(TEST_BASE, "GestionRiesgos")
    assert_it(os.path.isdir(path), "carpeta con nombre unido")
    assert_it(os.path.isfile(os.path.join(path, "models", "gestionriesgos_models.py")), "model correcto")

def test_version_with_dots():
    """Versión con puntos (v1.1) en rutas"""
    mc.create_structure(TEST_BASE, "Alertas", "v1.1")
    path = os.path.join(TEST_BASE, "Alertas", "api", "v1.1", "routes.py")
    assert_it(os.path.isfile(path), "routes.py en api/v1.1/")

def test_exports_and_utils_folders_created():
    """Las carpetas exports/ y utils/ también se crean"""
    mc.create_structure(TEST_BASE, "Analytics", "v1")
    base = os.path.join(TEST_BASE, "Analytics")
    assert_it(os.path.isdir(os.path.join(base, "exports")), "exports/ existe")
    assert_it(os.path.isdir(os.path.join(base, "utils")), "utils/ existe")

def test_all_init_files_exist():
    """Cada subcarpeta tiene su __init__.py"""
    mc.create_structure(TEST_BASE, "Eventos", "v1")
    base = os.path.join(TEST_BASE, "Eventos")
    for folder in ["api", "api/v1", "models", "repositories", "services", "validations", "exports", "utils"]:
        init = os.path.join(base, folder, "__init__.py")
        assert_it(os.path.isfile(init), f"__init__.py en {folder}/")

# ──────────────────────────────────────────────
# RUNNER
# ──────────────────────────────────────────────

if __name__ == "__main__":
    setup()

    TESTS = [
        ("capitalize_and_clean_folder_name",     test_capitalize_clean),
        ("Crear estructura v1",                  test_create_structure_v1),
        ("Crear estructura versión custom (v2)", test_create_structure_custom_version),
        ("No sobreescribir módulo existente",    test_create_structure_duplicate_returns_false),
        ("Contenido de __init__.py en subs",     test_init_files_content),
        ("Contenido de routes.py",               test_routes_content),
        ("Contenido de models.py (Pydantic)",    test_models_content),
        ("Contenido de validation.py",           test_validation_content),
        ("Agregar versión v1.1",                 test_add_version_to_existing_module),
        ("No duplicar versión existente",        test_add_duplicate_version_returns_false),
        ("README.md generado correctamente",     test_readme_generated),
        ("Append README sin borrar contenido",   test_readme_append_new_version),
        ("main.py nuevo con router versionado",  test_update_main_py_new),
        ("main.py acumula múltiples routers",    test_update_main_py_appends),
        ("Nombre de módulo multi-palabra",       test_multiword_module_name),
        ("Versión con puntos (v1.1)",            test_version_with_dots),
        ("Carpetas exports/ y utils/ creadas",   test_exports_and_utils_folders_created),
        ("Todos los __init__.py existen",        test_all_init_files_exist),
    ]

    print("\n" + "="*60)
    print("   🧪 TEST SUITE: modulecreator.py")
    print("="*60)

    for name, fn in TESTS:
        run_test(name, fn)

    print()
    for icon, name, detail in RESULTS:
        print(f"  {icon}  {name}")
        if detail:
            print(f"      ↳ {detail}")

    passed = sum(1 for r in RESULTS if r[0] == "✅")
    failed = sum(1 for r in RESULTS if r[0] == "❌")
    total = len(RESULTS)

    print()
    print("="*60)
    print(f"   Resultado: {passed}/{total} tests pasaron  |  {failed} fallaron")
    print("="*60)

    teardown()
    sys.exit(0 if failed == 0 else 1)
