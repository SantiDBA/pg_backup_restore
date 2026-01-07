@echo off
setlocal EnableDelayedExpansion

:: ==============================================================================
:: PostgreSQL Backup Runner for Windows Task Scheduler
:: ==============================================================================

:: --- CONFIGURATION (EDIT THESE) ---
set "PYTHON_EXE=python"
set "SCRIPT_PATH=%~dp0backup_postgres.py"
set "BACKUP_DIR=%~dp0backups"

:: PostgreSQL Bin Directory (Optional)
:: If PostgreSQL tools (pg_dump) are not in your PATH, 
:: set the directory where they are located.
:: Example: set "PG_BIN_DIR=C:\Program Files\PostgreSQL\16\bin"
set "PG_BIN_DIR="

set "DB_HOST=localhost"
set "DB_PORT=5432"
set "DB_NAME=my_database"
set "DB_USER=postgres"
set "DB_PASSWORD=my_password"
set "RETENTION=30"
set "LOG_FILE=%~dp0run_backup.log"

:: --- QUOTE STRIPPING (Ensure variables are clean before use) ---
set "PYTHON_EXE=!PYTHON_EXE:"=!"
set "SCRIPT_PATH=!SCRIPT_PATH:"=!"
set "BACKUP_DIR=!BACKUP_DIR:"=!"
set "PG_BIN_DIR=!PG_BIN_DIR:"=!"
set "DB_HOST=!DB_HOST:"=!"
set "DB_NAME=!DB_NAME:"=!"
set "DB_USER=!DB_USER:"=!"
set "DB_PASSWORD=!DB_PASSWORD:"=!"
set "LOG_FILE=!LOG_FILE:"=!"

:: Ensure we are in the script's directory
cd /d "%~dp0"


:: --- EXECUTION ---
echo Starting backup process. Logging to: "!LOG_FILE!"

:: Prepare arguments
set "ARG_BIN="
if not "!PG_BIN_DIR!"=="" set "ARG_BIN=--bin-dir "!PG_BIN_DIR!""

(
    echo.
    echo ==============================================================================
    echo BACKUP ATTEMPT START: %DATE% %TIME%
    echo ------------------------------------------------------------------------------
    echo SCRIPT:  "!SCRIPT_PATH!"
    echo PYTHON:  "!PYTHON_EXE!"
    echo BIN DIR: "!PG_BIN_DIR!"
    echo ------------------------------------------------------------------------------

    "!PYTHON_EXE!" "!SCRIPT_PATH!" ^
        --host "!DB_HOST!" ^
        --port "!DB_PORT!" ^
        --database "!DB_NAME!" ^
        --username "!DB_USER!" ^
        --password "!DB_PASSWORD!" ^
        --backup-dir "!BACKUP_DIR!" ^
        --retention-days !RETENTION! ^
        !ARG_BIN!

    set EXIT_CODE=!ERRORLEVEL!

    if !EXIT_CODE! NEQ 0 (
        echo [ERROR] Backup script failed with exit code !EXIT_CODE!
    ) else (
        echo [SUCCESS] Backup completed successfully.
    )
    
    echo ==============================================================================
) >> "!LOG_FILE!" 2>&1

if !EXIT_CODE! NEQ 0 (
    echo [ERROR] Backup failed. See "!LOG_FILE!" for details.
    exit /b !EXIT_CODE!
)

echo [SUCCESS] Backup finished.
exit /b 0
