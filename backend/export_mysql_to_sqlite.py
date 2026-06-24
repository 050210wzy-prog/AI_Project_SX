from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker


def main() -> None:
    os.environ["DATABASE_BACKEND"] = "mysql"
    os.environ["SQLITE_PATH"] = "data/app.db"

    from app.core.config import Settings
    from app.core.database import Base
    from app.models import models  # noqa: F401

    mysql_settings = Settings()
    mysql_url = mysql_settings.database_url
    sqlite_path = Path("data/app.db")
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    if sqlite_path.exists():
        sqlite_path.unlink()

    mysql_engine = create_engine(mysql_url, pool_pre_ping=True)
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path.as_posix()}", connect_args={"check_same_thread": False})

    Base.metadata.create_all(bind=sqlite_engine)
    mysql_session = sessionmaker(bind=mysql_engine)()
    sqlite_session = sessionmaker(bind=sqlite_engine)()
    inspector = inspect(mysql_engine)

    exported = []
    try:
        for table in Base.metadata.sorted_tables:
            table_name = table.name
            if table_name not in inspector.get_table_names():
                continue
            rows = [dict(row._mapping) for row in mysql_session.execute(text(f"SELECT * FROM {table_name}")).all()]
            if rows:
                sqlite_session.execute(table.insert(), rows)
            exported.append((table_name, len(rows)))
        sqlite_session.commit()
    finally:
        mysql_session.close()
        sqlite_session.close()

    print(f"SQLite exported: {sqlite_path.resolve()}")
    for table_name, count in exported:
        print(f"{table_name}: {count}")


if __name__ == "__main__":
    main()
