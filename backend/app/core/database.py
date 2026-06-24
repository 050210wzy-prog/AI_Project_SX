from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
if settings.use_sqlite:
    Path(settings.sqlite_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models.models import seed_defaults  # noqa: WPS433

    backend = "SQLite" if settings.use_sqlite else "MySQL"
    print(f"Database backend: {backend}")
    Base.metadata.create_all(bind=engine)
    _ensure_student_record_columns()
    _ensure_grade_record_columns()
    with SessionLocal() as db:
        seed_defaults(db)


def _ensure_student_record_columns() -> None:
    columns = {
        "student_no": "VARCHAR(50) NULL",
        "province": "VARCHAR(50) NULL",
        "city": "VARCHAR(80) NULL",
        "department": "VARCHAR(120) NULL",
        "remark": "TEXT NULL",
        "id_card": "VARCHAR(50) NULL",
        "birthday": "VARCHAR(50) NULL",
        "gender": "VARCHAR(20) NULL",
        "admission_type": "VARCHAR(120) NULL",
        "admission_batch": "VARCHAR(120) NULL",
        "subject": "VARCHAR(80) NULL",
        "major_code": "VARCHAR(50) NULL",
        "political_status": "VARCHAR(80) NULL",
        "ethnicity": "VARCHAR(80) NULL",
        "candidate_type": "VARCHAR(120) NULL",
        "graduate_type": "VARCHAR(120) NULL",
        "middle_school": "VARCHAR(180) NULL",
        "foreign_language": "VARCHAR(80) NULL",
        "area_code": "VARCHAR(50) NULL",
        "area_name": "VARCHAR(120) NULL",
        "address": "TEXT NULL",
        "postal_code": "VARCHAR(30) NULL",
        "receiver": "VARCHAR(80) NULL",
        "score": "FLOAT NULL",
        "application_choice": "VARCHAR(80) NULL",
        "first_major": "VARCHAR(120) NULL",
        "second_major": "VARCHAR(120) NULL",
        "third_major": "VARCHAR(120) NULL",
        "fourth_major": "VARCHAR(120) NULL",
        "fifth_major": "VARCHAR(120) NULL",
        "sixth_major": "VARCHAR(120) NULL",
        "adjustment": "VARCHAR(50) NULL",
        "chinese_score": "FLOAT NULL",
        "math_score": "FLOAT NULL",
        "foreign_score": "FLOAT NULL",
        "comprehensive_score": "FLOAT NULL",
        "subject_name": "VARCHAR(80) NULL",
    }
    with engine.begin() as conn:
        existing = _existing_columns(conn, "student_records")
        for name, definition in columns.items():
            if name not in existing:
                conn.exec_driver_sql(f"ALTER TABLE student_records ADD COLUMN {name} {_column_definition(definition)}")


def _ensure_grade_record_columns() -> None:
    columns = {
        "student_id": "INT NULL",
        "exam_no": "VARCHAR(80) NULL",
        "class_name": "VARCHAR(80) NULL",
        "major": "VARCHAR(120) NULL",
        "process_score": "FLOAT NOT NULL DEFAULT 0",
        "final_score": "FLOAT NOT NULL DEFAULT 0",
        "practice_score": "FLOAT NOT NULL DEFAULT 0",
        "total_score": "FLOAT NOT NULL DEFAULT 0",
        "assessment": "VARCHAR(80) NOT NULL DEFAULT '平时+期末'",
        "status": "VARCHAR(50) NOT NULL DEFAULT '正常'",
    }
    with engine.begin() as conn:
        existing = _existing_columns(conn, "grade_records")
        for name, definition in columns.items():
            if name not in existing:
                conn.exec_driver_sql(f"ALTER TABLE grade_records ADD COLUMN {name} {_column_definition(definition)}")


def _existing_columns(conn, table_name: str) -> set[str]:
    if settings.use_sqlite:
        return {row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table_name})")}
    return {
        row[0]
        for row in conn.exec_driver_sql(
            f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table_name}'
            """
        )
    }


def _column_definition(definition: str) -> str:
    if not settings.use_sqlite:
        return definition
    return (
        definition.replace("VARCHAR(50)", "TEXT")
        .replace("VARCHAR(80)", "TEXT")
        .replace("VARCHAR(120)", "TEXT")
        .replace("VARCHAR(180)", "TEXT")
        .replace("INT", "INTEGER")
        .replace("FLOAT", "REAL")
    )
