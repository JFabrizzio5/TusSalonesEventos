import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from factory.app import create_requirements
from factory.db import create_database_config
from factory.envs import create_env_files, create_gitignore
from factory.todo import create_todo_module


def test_excel_scaffold_generation(tmp_path):
    project_path = tmp_path / "ExcelService"
    project_path.mkdir()

    create_env_files(str(project_path), "excel", base_port=9010, description="Excel-first service")
    create_gitignore(str(project_path))
    create_database_config(str(project_path), "excel")
    create_requirements(str(project_path), "excel")
    create_todo_module(str(project_path), "excel")

    env_dev = (project_path / ".env.dev").read_text()
    gitignore = (project_path / ".gitignore").read_text()
    database_py = (project_path / "config" / "database.py").read_text()
    requirements = (project_path / "requirements.txt").read_text()
    todo_routes = (project_path / "modules" / "todo" / "api" / "v1" / "routes.py").read_text()

    assert "EXCEL_STORAGE_PATH=storage/excelservice.xlsx" in env_dev
    assert "EXCEL_SHEET_DEFAULT=sheet1" in env_dev
    assert "storage/*.xlsx" in gitignore
    assert "async def get_excel_workbook()" in database_py
    assert "async def append_excel_row" in database_py
    assert "openpyxl" in requirements
    assert "sqlalchemy" not in requirements
    assert "append_excel_row" in todo_routes
    assert "list_excel_rows" in todo_routes
    assert (project_path / "storage" / ".gitkeep").exists()
