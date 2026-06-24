@echo off
cd /d %~dp0
if not exist .env copy .env.example .env
echo Starting FastAPI backend: http://127.0.0.1:8000
D:\python\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
