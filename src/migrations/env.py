from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Calculate the path to the directory above "migrations" and add it to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Now we can import the Flask application and the database instance
from app import app, db

# Import your models here to include them in the migration context
# from app import Model1, Model2, ...

config = context.config

# If Alembic is configured to use logging, this line sets up loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use the SQLALCHEMY_DATABASE_URI from your Flask app's config
sqlalchemy_url = app.config['SQLALCHEMY_DATABASE_URI']
config.set_main_option('sqlalchemy.url', sqlalchemy_url)

# Alembic needs access to your models' metadata to generate migrations
target_metadata = db.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.', poolclass=pool.NullPool,)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()