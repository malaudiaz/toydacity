from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Añade esto para importar tus modelos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importa tu Base (de donde heredan los modelos)
from app.database import Base  # Ajusta esta ruta
from app.modules.auth.models import *  # Importa todos tus modelos

# Configuración del entorno
config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata  # Apunta a los metadatos de tus modelos

def run_migrations_offline():
    # Configuración para migraciones offline
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

def run_migrations_online():
    # Configuración para migraciones online
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()