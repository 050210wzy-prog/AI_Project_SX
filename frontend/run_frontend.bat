@echo off
cd /d %~dp0
set NO_UPDATE_NOTIFIER=1
set npm_config_cache=%CD%\.npm-cache
set npm_config_prefix=%CD%\.npm-global
set XDG_CONFIG_HOME=%CD%\.config
set npm_config_update_notifier=false
if not exist node_modules (
  echo Installing frontend dependencies. This may take a few minutes.
  npm install --registry=https://registry.npmmirror.com --cache "%CD%\.npm-cache" --no-audit --no-fund
  if errorlevel 1 (
    echo Dependency installation failed.
    echo Please run: npm install --registry=https://registry.npmmirror.com --cache "%CD%\.npm-cache" --no-audit --no-fund
    pause
    exit /b 1
  )
)
echo Starting Vue frontend: http://localhost:5173
npm run dev
