"""Configuración de conexión a MySQL."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote_plus

from dotenv import load_dotenv

from src.config.paths import project_root

load_dotenv(project_root() / ".env")


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    return value.strip()


@dataclass(frozen=True)
class MySQLSettings:
    host: str
    port: int
    user: str
    password: str
    database: str

    def _auth_url(self) -> str:
        user = quote_plus(self.user)
        password = quote_plus(self.password)
        return f"{user}:{password}@{self.host}:{self.port}"

    @property
    def server_url(self) -> str:
        """URL sin base de datos (para crear la BD)."""
        return f"mysql+pymysql://{self._auth_url()}/?charset=utf8mb4"

    @property
    def database_url(self) -> str:
        """URL con la base de datos del proyecto."""
        return f"mysql+pymysql://{self._auth_url()}/{self.database}?charset=utf8mb4"


def get_mysql_settings() -> MySQLSettings:
    password = _env("MYSQL_PASSWORD")
    if not password:
        raise ValueError(
            "Falta MYSQL_PASSWORD. Copia .env.example a .env y rellena tus credenciales."
        )
    return MySQLSettings(
        host=_env("MYSQL_HOST", "localhost") or "localhost",
        port=int(_env("MYSQL_PORT", "3306") or "3306"),
        user=_env("MYSQL_USER", "root") or "root",
        password=password,
        database=_env("MYSQL_DATABASE", "insightmarket") or "insightmarket",
    )
