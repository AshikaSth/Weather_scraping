from __future__ import with_statement
import logging
from logging.config import fileConfig

from flask import Flask
from alembic import context

# your app factory and db
from app import create_app, db
from app.models.weather import WeatherRecord  # import all models here

# Alembic config
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# this is the important part: Alembic needs the metadata
target_metadata = db.metadata

# offline migrations
def run_migrations_offline():
    url = str(app.config["SQLALCHEMY_DATABASE_URI"]).replace('%', '%%')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

# online migrations
def run_migrations_online():
    connectable = db.engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True  # important if you add columns with new types
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()