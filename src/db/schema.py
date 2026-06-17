"""Esquema y operaciones de la tabla products."""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    text,
)
from sqlalchemy.engine import Engine

from src.db.config import MySQLSettings, get_mysql_settings

metadata = MetaData()

products_table = Table(
    "products",
    metadata,
    Column("product_id", String(50), primary_key=True),
    Column("product_name", String(255), nullable=False),
    Column("category", String(100), nullable=False),
    Column("price_usd", Float, nullable=False),
    Column("rating", Float),
    Column("review_count", Integer),
    Column("brand", String(100)),
    Column("stock", Integer, nullable=False),
    Column("review_author", String(120)),
    Column("short_review", Text),
    Column("is_recommended", Boolean),
)


def create_database_if_not_exists(settings: MySQLSettings | None = None) -> None:
    settings = settings or get_mysql_settings()
    engine = create_engine(settings.server_url)
    with engine.connect() as conn:
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{settings.database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        conn.commit()


def create_tables(engine: Engine) -> None:
    metadata.create_all(engine)


def drop_products_table(engine: Engine) -> None:
    products_table.drop(engine, checkfirst=True)
