@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "REPO_DIR=%~dp0"
if "%REPO_DIR:~-1%"=="\" set "REPO_DIR=%REPO_DIR:~0,-1%"
set "REPO_SLASH=%REPO_DIR:\=/%"
set "PY_CMD=%REPO_SLASH%/MCP_SERVER/.venv/Scripts/python.exe"

echo ==================================================
echo   Jarvis Target-R Team Setup (Windows)
echo ==================================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.11+ not found. Please install Python 3.11+ and check "Add python.exe to PATH".
    pause
    exit /b 1
)

where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found. Please install Git for Windows first.
    pause
    exit /b 1
)

echo [1/3] Creating Python virtual environment in MCP_SERVER\.venv ...
if not exist "%REPO_DIR%\MCP_SERVER\.venv\Scripts\python.exe" (
    python -m venv "%REPO_DIR%\MCP_SERVER\.venv"
)

echo [2/3] Installing MCP Server dependencies ...
set "INSTALL_OK=0"
if exist "%REPO_DIR%\MCP_SERVER\.venv\Scripts\python.exe" (
    "%REPO_DIR%\MCP_SERVER\.venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
    "%REPO_DIR%\MCP_SERVER\.venv\Scripts\python.exe" -m pip install -e "%REPO_DIR%\MCP_SERVER" google-auth
    if not errorlevel 1 set "INSTALL_OK=1"
)

if "%INSTALL_OK%"=="0" (
    echo [INFO] Virtual environment blocked or unavailable, falling back to system Python...
    python -m pip install -e "%REPO_DIR%\MCP_SERVER" google-auth
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    set "SYS_PY="
    for /f "delims=" %%I in ('where python') do if not defined SYS_PY set "SYS_PY=%%I"
    set "PY_CMD=!SYS_PY:\=/!"
)

echo [3/3] Checking .env configuration ...
if not exist "%REPO_DIR%\.env" (
    copy "%REPO_DIR%\.env.example" "%REPO_DIR%\.env" >nul
    echo   Created .env from .env.example ^(Please fill in your team tokens and JSON path!^)
) else (
    echo   .env already exists ^(skipped copy^).
)

echo.
echo ==================================================
echo   Setup Complete!
echo ==================================================
echo.
echo Copy this MCP JSON block into Antigravity Desktop ^(Manage MCP Servers -^> Raw Config^):
echo.
echo {
echo   "mcpServers": {
echo     "jarvis-targetr": {
echo       "command": "%PY_CMD%",
echo       "args": ["-m", "jarvis_mcp.server"],
echo       "cwd": "%REPO_SLASH%/MCP_SERVER",
echo       "env": {
echo         "PYTHONPATH": "%REPO_SLASH%/MCP_SERVER"
echo       }
echo     }
echo   }
echo }
echo.
pause
