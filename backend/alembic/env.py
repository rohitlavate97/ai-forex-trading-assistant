import asyncio
from logging.config import fileConfig
from alembic import context

# Interpret the config file for Python logging.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import our metadata and models
from src.core.database import Base
from src.modules.auth.models import User  # Registers User model in metadata
from src.modules.journal.models import JournalEntry  # Registers JournalEntry model in metadata

target_metadata = Base.metadata

# Inject the dynamic database connection URL from Settings
from src.core.config import settings
config.set_main_option("sqlalchemy.url", settings.async_database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations inside a sync context using the async connection wrapper."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using the shared async_engine."""
    from src.core.database import async_engine

    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await async_engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Run the async online migration
    asyncio.run(run_migrations_online())
