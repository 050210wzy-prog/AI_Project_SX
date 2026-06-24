# 联调检查记录

## 当前架构

项目已切换为前后端分离版本：

- 后端：`backend/`，FastAPI + SQLAlchemy + MySQL
- 前端：`frontend/`，Vue 3 + Element Plus + Pinia + Vue Router
- 数据库：MySQL，建表脚本为 `mysql_schema.sql`

旧版 Streamlit 单体应用入口已移除。

## MySQL

运行前请确认 `backend/.env` 中的 MySQL 配置：

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=admission_system
```

如数据库不存在，执行：

```sql
CREATE DATABASE admission_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后执行根目录的 `mysql_schema.sql`。

连接检查：

```bat
cd C:\Users\30587\Desktop\222
D:\python\python.exe backend\check_mysql.py
```

## 后端

```bat
cd C:\Users\30587\Desktop\222\backend
run_backend.bat
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## 前端

```bat
cd C:\Users\30587\Desktop\222\frontend
run_frontend.bat
```

前端地址：

```text
http://localhost:5173
```
