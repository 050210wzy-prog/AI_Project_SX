from sqlalchemy import text

from app.core.database import SessionLocal, engine, init_db
from app.models.models import seed_defaults


def main() -> None:
    init_db()
    with SessionLocal() as db:
        seed_defaults(db)
        db.execute(text("SELECT 1"))
    print("数据库初始化完成：已建表并写入基础数据。")


if __name__ == "__main__":
    main()
