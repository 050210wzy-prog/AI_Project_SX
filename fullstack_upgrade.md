# FastAPI + Vue 3 + Element Plus + MySQL 版本说明

当前项目只保留新版前后端分离架构：

```text
backend/   FastAPI 后端，负责登录、招生数据、官网内容、AI 问答和管理后台接口
frontend/  Vue 3 + Element Plus 前端，负责官网门户、招生问答和管理后台界面
```

旧版 Streamlit 单体应用已经移除。

## 1. 准备 MySQL

创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS admission_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后执行根目录的建表脚本：

```text
mysql_schema.sql
```

## 2. 启动后端

进入后端目录：

```bat
cd C:\Users\30587\Desktop\222\backend
```

确认 `.env` 中的 MySQL 配置：

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=admission_system
```

安装依赖：

```bat
D:\python\python.exe -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt
```

启动：

```bat
run_backend.bat
```

后端地址：

```text
http://127.0.0.1:8000
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

默认管理员：

```text
admin / admin123
```

## 3. 启动前端

进入前端目录：

```bat
cd C:\Users\30587\Desktop\222\frontend
```

启动：

```bat
run_frontend.bat
```

前端地址：

```text
http://localhost:5173
```

## 4. 主要功能

- Vue 官网门户：首页轮播、新闻公告、站内搜索
- Vue 招生问答：调用 FastAPI `/api/chat`
- Vue 管理后台：数据看板、招生管理、官网管理、咨询工单
- FastAPI 登录认证：JWT Token
- FastAPI 招生接口：专业库、录取分数、分数推荐
- FastAPI 官网接口：轮播图、文章列表、文章详情、内容审核
- FastAPI AI 接口：兼容 OpenAI 风格接口和 Spark-X2 参数
- MySQL 数据模型：用户、专业、分数、招生计划、官网文章、附件、轮播、工单
