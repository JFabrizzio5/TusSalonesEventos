import asyncio
import logging
import os
import importlib
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import init_sql_engine, _AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seeder_runner")

async def run_modular_seeds():
    logger.info("🚀 Iniciando Seeder Runner (Modular Discovery)...")
    await init_sql_engine()
    
    # Importar después de inicializar para obtener la referencia correcta
    from config.database import _AsyncSessionLocal
    
    modules_path = "modules"
    if not os.path.exists(modules_path):
        logger.warning("⚠️ No se encontró la carpeta 'modules'.")
        return

    async with _AsyncSessionLocal() as session:
        try:
            # 1. Descubrir semillas en módulos
            for module_name in os.listdir(modules_path):
                seeds_dir = os.path.join(modules_path, module_name, "seeds")
                if os.path.isdir(seeds_dir):
                    logger.info(f"📁 Buscando semillas en módulo: {module_name}")
                    for seed_file in os.listdir(seeds_dir):
                        if seed_file.endswith("_seed.py"):
                            seed_name = seed_file[:-3]
                            module_spec = f"modules.{module_name}.seeds.{seed_name}"
                            try:
                                seed_mod = importlib.import_module(module_spec)
                                if hasattr(seed_mod, "seed"):
                                    logger.info(f"🌱 Ejecutando semilla: {seed_name}...")
                                    await seed_mod.seed(session)
                                else:
                                    logger.warning(f"⚠️ El archivo {seed_file} no tiene una función 'seed(session)'.")
                            except Exception as e:
                                logger.error(f"❌ Error importando/ejecutando {module_spec}: {e}")
            
            await session.commit()
            logger.info("✅ Todos los seeders han finalizado.")
            
        except Exception as e:
            logger.error(f"💥 Error crítico en Seeder Runner: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(run_modular_seeds())
