@echo off
cd /d %~dp0
set NO_UPDATE_NOTIFIER=1
set XDG_CONFIG_HOME=%CD%\.config
set npm_config_cache=%CD%\.npm-cache
set npm_config_prefix=%CD%\.npm-global
set npm_config_update_notifier=false
echo Building Vue frontend...
D:\NodeJs\node.exe .\build.mjs
if errorlevel 1 (
  echo Frontend build failed.
  pause
  exit /b 1
)
echo Frontend build completed: %CD%\dist
