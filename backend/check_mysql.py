from __future__ import annotations

import sys

import pymysql
from pymysql.err import MySQLError

from app.core.config import settings


def main() -> int:
    try:
        connection = pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            charset="utf8mb4",
            connect_timeout=5,
        )
    except MySQLError as exc:
        print(f"MySQL connection failed: {exc}")
        print("Check MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, and MYSQL_PORT in backend/.env.")
        return 1

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            cursor.execute("SHOW DATABASES LIKE %s", (settings.mysql_database,))
            database_exists = cursor.fetchone() is not None

    print(f"MySQL is reachable: {version}")
    if database_exists:
        print(f"Database exists: {settings.mysql_database}")
        return 0

    print(f"Database is missing: {settings.mysql_database}")
    print(f"Create it with: CREATE DATABASE {settings.mysql_database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
