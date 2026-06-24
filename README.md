# 安徽交通职业技术学院官网与招生咨询系统

本项目是一个前后端分离的官网与招生咨询系统，当前版本已经移除旧版 Streamlit 单体应用，统一使用 FastAPI 后端和 Vue 3 前端。

## 技术架构

- `backend/`：FastAPI + SQLAlchemy + MySQL
- `frontend/`：Vue 3 + Element Plus + Pinia + Vue Router
- `mysql_schema.sql`：MySQL 数据库建表脚本
- `uploads/`：后台上传文件目录

## 主要功能

- 官网首页、二级栏目、学院内页、服务页面和英文官网
- 新闻、通知、轮播图、栏目、附件等官网内容管理
- 招生专业库、历年分数线、招生计划和智能咨询
- 后台管理系统，包括数据看板、招生管理、官网管理、工单管理等
- 信息门户、电子邮箱、WebVPN 校内资源入口
- MySQL 数据存储，支持后台内容实时更新到前端页面

## 智慧官网创新中心

前端访问地址：

```text
http://localhost:5173/innovation
```

当前已实现 8 个创新功能：

- 招生智能推荐系统：根据省份、科类、分数和兴趣生成冲稳保专业建议。
- 专业画像页面：展示专业简介、核心课程、就业岗位、实训条件、合作企业和录取趋势。
- 官网内容同步与审核看板：聚合后台文章、通知、图片资源和最新内容。
- 校园服务统一入口：按学生、教师、考生、校友、访客身份展示常用服务。
- 可视化数据大屏：展示文章、专业、咨询、工单和热门专业数据。
- AI 招生问答增强版：展示问答来源引用，提升回答可信度。
- VR/地图式校园导览：展示新桥校区、包河校区、校园地点和交通指引。
- 英文官网自动内容映射：把中文内容映射成英文官网草稿，便于后续审核发布。

## 运行前准备

1. 安装并启动 MySQL。

2. 创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS admission_system
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

3. 执行根目录下的 `mysql_schema.sql` 建表脚本。

4. 检查后端配置文件 `backend/.env`：

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=admission_system
```

当前本机 MySQL 密码如仍使用之前配置，应为：

```text
MYSQL_PASSWORD=050210wzy.
```

## 启动后端

进入后端目录：

```bat
cd C:\Users\30587\Desktop\222\backend
```

启动服务：

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

## 启动前端

另开一个命令行窗口，进入前端目录：

```bat
cd C:\Users\30587\Desktop\222\frontend
```

启动服务：

```bat
run_frontend.bat
```

前端地址：

```text
http://localhost:5173
```

## 默认管理员

系统初始化时会创建一个默认管理员：

```text
账号：admin
密码：admin123
```

正式部署前请在后台或数据库中修改默认密码，不要保留公开默认口令。

## 常用命令

安装后端依赖：

```bat
cd C:\Users\30587\Desktop\222\backend
D:\python\python.exe -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt
```

安装前端依赖：

```bat
cd C:\Users\30587\Desktop\222\frontend
npm install --registry=https://registry.npmmirror.com --cache "%CD%\.npm-cache" --no-audit --no-fund
```

构建前端：

```bat
cd C:\Users\30587\Desktop\222\frontend
npm run build
```

如果构建时报 `EPERM: operation not permitted, lstat 'C:\Users\30587'`，说明当前 Windows 用户目录权限或 Node.js 安装环境阻止 npm 读取用户目录。项目已把 npm 缓存和配置目录改到 `frontend/.npm-cache`、`frontend/.config`，仍报错时建议使用管理员权限终端，或重新安装 Node.js 到普通英文路径后再构建。

检查 MySQL 连接：

```bat
cd C:\Users\30587\Desktop\222
D:\python\python.exe backend\check_mysql.py
```

## 部署注意事项

- 后台上传文件现在使用 `/uploads/文件名` 相对地址，部署时需要确保后端静态文件挂载正常。
- 前端开发环境通过 Vite 代理访问 `/api`，生产环境需要在 Nginx 或服务器中配置 `/api` 转发到 FastAPI。
- `backend/.env` 中包含数据库密码和密钥，不要上传到公开仓库。
- 正式部署时应修改 `SECRET_KEY`、管理员密码和数据库账号密码。
- 如果要接入学校真实 WebVPN、邮箱或统一身份认证，需要学校提供实际系统地址和接口配置。

### Render 无云 MySQL 部署

如果只想把后端部署到 Render 演示，又没有云 MySQL，可以让后端使用 SQLite。Render 后端 Web Service 环境变量填写：

```text
APP_NAME=安徽交通职业技术学院官网与招生咨询系统
DEBUG=false
SECRET_KEY=在 Render 中 Generate 生成
DATABASE_BACKEND=sqlite
SQLITE_PATH=data/app.db
ZHIPU_API_KEY=你的智谱 API Key
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
ZHIPU_MODEL=glm-4-flash
CORS_ORIGINS=*
EHALL_URL=https://ehall.acvtc.edu.cn/
OA_URL=https://jyoa.acvtc.edu.cn/
```

此模式不需要填写 `MYSQL_HOST`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE`。本地 `.env` 仍配置 MySQL 时，本机运行会继续使用 MySQL。

注意：Render 免费实例的本地 SQLite 文件不适合长期保存正式数据，适合项目演示和答辩。正式上线仍建议使用云 MySQL。

## 初始化、测试与部署辅助

初始化数据库和基础数据：

```bat
cd C:\Users\30587\Desktop\222\backend
D:\python\python.exe init_db.py
```

运行后端冒烟测试：

```bat
cd C:\Users\30587\Desktop\222\backend
D:\python\python.exe smoke_test.py
```

生产部署可参考根目录下的：

```text
deploy_nginx.example.conf
```

后台新增“创新中心”管理入口，可维护 8 项创新功能开关、排序、说明，以及 WebVPN、邮箱、信息门户等真实系统对接地址。

## 目录说明

## 官网实时采集

后台入口：`http://localhost:5173/admin/crawler`

功能说明：

- 可配置学校新闻、通知公告、招标采购、部门动态等采集源。
- 可手动运行单个采集源或全部采集源。
- 采集内容写入官网文章库，并可设置为“待审核”“已发布”或“草稿”。
- 按原文链接去重，避免重复导入。
- 采集记录支持查看原文和生成后的文章详情。

建议流程：配置采集源 -> 运行采集 -> 进入官网管理审核 -> 发布到新版官网。

## 案例 A：校园生活百事通助手

本项目已将实训指导书“案例 A——校园生活百事通助手”集成到现有 `/chat` 页面中，不再额外创建 Streamlit 单体页面。

已实现：

- `backend/data/campus_data.csv`：20 条校园生活问答数据。
- `backend/scripts/split_campus_data.py`：文档切分示例脚本。
- `backend/scripts/build_campus_vector_db.py`：构建 `campus_life_kb` Chroma 向量库。
- `backend/scripts/test_campus_retrieve.py`：检索测试脚本。
- `backend/scripts/campus_rag_demo.py`：RAG 问答演示脚本。
- `backend/scripts/campus_agent_demo.py`：ReAct 工具调用与多轮记忆演示脚本。
- `/chat` 页面：左侧切换到“校园生活”模式即可使用。

构建校园生活向量库：

```bat
cd C:\Users\30587\Desktop\222\backend
D:\python\python.exe scripts\build_campus_vector_db.py
```

测试检索：

```bat
cd C:\Users\30587\Desktop\222\backend
D:\python\python.exe scripts\test_campus_retrieve.py
```

测试报告：

```text
reports/campus_life_case_a_test_report.md
```

可选模型配置：

```text
SPARK_API_PASSWORD=你的星火APIpassword
DEEPSEEK_API_KEY=你的DeepSeek API Key
ZHIPU_API_KEY=你的智谱 API Key
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
ZHIPU_MODEL=glm-4-flash
```

- `backend/app/api/`：后端接口
- `backend/app/models/`：数据库模型
- `backend/app/core/`：数据库、配置、认证等核心模块
- `frontend/src/views/`：前端页面
- `frontend/src/components/`：通用组件
- `frontend/src/router/`：前端路由
- `frontend/src/stores/`：Pinia 状态管理
- `uploads/`：上传文件存储目录
