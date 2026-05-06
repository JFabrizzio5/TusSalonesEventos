import os

def create_todo_module(project_path, db_type):
    """Genera un módulo inicial 'Todo' con soporte SQL o Excel."""
    if db_type not in ["sql", "both", "excel"]:
        return

    todo_path = os.path.join(project_path, "modules", "todo")
    os.makedirs(os.path.join(todo_path, "models"), exist_ok=True)
    os.makedirs(os.path.join(todo_path, "api", "v1"), exist_ok=True)
    os.makedirs(os.path.join(todo_path, "services"), exist_ok=True)
    os.makedirs(os.path.join(todo_path, "repositories"), exist_ok=True)

    if db_type in ["sql", "both"]:
        # 1. SQLAlchemy Model
        model_content = """from sqlalchemy import Column, Integer, String, Boolean, DateTime
from config.database import Base
from datetime import datetime

class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
"""
        with open(os.path.join(todo_path, "models", "models.py"), "w") as f:
            f.write(model_content)

        # 2. Routes (CRUD)
        routes_content = """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_sql_db
from modules.todo.models.models import Todo
from sqlalchemy import select

router = APIRouter()

@router.get("/")
async def list_todos(db: AsyncSession = Depends(get_sql_db)):
    result = await db.execute(select(Todo))
    return result.scalars().all()

@router.post("/")
async def create_todo(title: str, description: str = None, db: AsyncSession = Depends(get_sql_db)):
    todo = Todo(title=title, description=description)
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo
"""
        with open(os.path.join(todo_path, "api", "v1", "routes.py"), "w") as f:
            f.write(routes_content)
    else:
        routes_content = """from fastapi import APIRouter
from config.database import append_excel_row, ensure_excel_sheet, list_excel_rows

router = APIRouter()
SHEET_NAME = "todos"
SHEET_HEADERS = ["title", "description", "completed"]

@router.get("/")
async def list_todos():
    await ensure_excel_sheet(SHEET_NAME, SHEET_HEADERS)
    return await list_excel_rows(SHEET_NAME)

@router.post("/")
async def create_todo(title: str, description: str = None):
    await ensure_excel_sheet(SHEET_NAME, SHEET_HEADERS)
    todo = {"title": title, "description": description or "", "completed": False}
    await append_excel_row(SHEET_NAME, todo)
    return todo
"""
        with open(os.path.join(todo_path, "api", "v1", "routes.py"), "w") as f:
            f.write(routes_content)

    # Init files
    for root, dirs, files in os.walk(todo_path):
        for d in dirs:
            open(os.path.join(root, d, "__init__.py"), "a").close()
    open(os.path.join(todo_path, "__init__.py"), "a").close()
