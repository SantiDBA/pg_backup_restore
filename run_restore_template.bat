@echo off
setlocal EnableDelayedExpansion

:: ==============================================================================
:: PostgreSQL Restore Runner for Windows
:: ==============================================================================

:: --- CONFIGURATION (EDIT THESE) ---
:: Note: The script will automatically handle quotes if you include them.
set "PYTHON_EXE=python"
set "SCRIPT_PATH=%~dp0restore_postgres.py"

:: PostgreSQL Bin Directory (Optional)
:: Example: set "PG_BIN_DIR=C:\Program Files\PostgreSQL\16\bin"
set "PG_BIN_DIR="

:: Database Connection Details
set "DB_HOST=localhost"
set "DB_PORT=5432"
set "DB_NAME=my_database"
set "DB_USER=postgres"
set "DB_PASSWORD=my_password"

:: RESTORE FILE (Provide the path to the .zip backup file)
set "ZIP_FILE="

:: Auto-confirm destructive operations (1 = Yes, 0 = Ask)
set "AUTO_CONFIRM=0"

:: --- LOGGING SETUP ---
set "LOG_FILE=%~dp0run_restore.log"

:: --- QUOTE STRIPPING ---
set "PYTHON_EXE=!PYTHON_EXE:"=!"
set "SCRIPT_PATH=!SCRIPT_PATH:"=!"
set "PG_BIN_DIR=!PG_BIN_DIR:"=!"
set "DB_HOST=!DB_HOST:"=!"
set "DB_NAME=!DB_NAME:"=!"
set "DB_USER=!DB_USER:"=!"
set "DB_PASSWORD=!DB_PASSWORD:"=!"
set "ZIP_FILE=!ZIP_FILE:"=!"
set "LOG_FILE=!LOG_FILE:"=!"

:: Ensure we are in the script's directory
cd /d "%~dp0"

:: --- DIAGNOSTICS ---
echo Starting restore process...
echo Python: "!PYTHON_EXE!"
echo Script: "!SCRIPT_PATH!"
echo Log:    "!LOG_FILE!"

:: Check if ZIP_FILE is set
if "!ZIP_FILE!"=="" (
    echo [ERROR] ZIP_FILE variable is empty in the script.
    echo Please edit run_restore_template.bat and set the ZIP_FILE path.
    pause
    exit /b 1
)

:: Check if ZIP_FILE exists
if not exist "!ZIP_FILE!" (
    echo [ERROR] Backup file not found: "!ZIP_FILE!"
    pause
    exit /b 1
)

:: Prepare arguments
set "ARG_YES="
if "!AUTO_CONFIRM!"=="1" set "ARG_YES=--yes"

set "ARG_BIN="
if not "!PG_BIN_DIR!"=="" set "ARG_BIN=--bin-dir "!PG_BIN_DIR!""

:: --- LOG HEADERS ---
(
    echo.
    echo ==============================================================================
    echo RESTORE ATTEMPT START: %DATE% %TIME%
    echo ------------------------------------------------------------------------------
    echo SCRIPT:   "!SCRIPT_PATH!"
    echo PYTHON:   "!PYTHON_EXE!"
    echo ZIP FILE: "!ZIP_FILE!"
    echo DATABASE: "!DB_NAME!"
    echo BIN DIR:  "!PG_BIN_DIR!"
    echo ------------------------------------------------------------------------------
) >> "!LOG_FILE!" 2>&1

:: --- EXECUTION (INTERACTIVE) ---
:: We don't redirect this block so the user can see prompts and provide input.
:: We use a temporary file to capture the output of this specific command to the log as well.
set "TEMP_LOG=%TEMP%\restore_output_%RANDOM%.log"

"!PYTHON_EXE!" "!SCRIPT_PATH!" ^
    --host "!DB_HOST!" ^
    --port "!DB_PORT!" ^
    --target-database "!DB_NAME!" ^
    --username "!DB_USER!" ^
    --password "!DB_PASSWORD!" ^
    --zip-file "!ZIP_FILE!" ^
    !ARG_YES! ^
    !ARG_BIN! | powershell -Command "$input | Tee-Object -FilePath '!TEMP_LOG!'"

set EXIT_CODE=!ERRORLEVEL!

:: --- APPEND TEMP LOG TO MAIN LOG AND CLEAN UP ---
if exist "!TEMP_LOG!" (
    type "!TEMP_LOG!" >> "!LOG_FILE!" 2>&1
    del "!TEMP_LOG!"
)

:: --- LOG FOOTER ---
(
    if !EXIT_CODE! NEQ 0 (
        echo [ERROR] Restore script failed with exit code !EXIT_CODE!
    ) else (
        echo [SUCCESS] Restore completed successfully.
    )
    echo ==============================================================================
) >> "!LOG_FILE!" 2>&1

if !EXIT_CODE! NEQ 0 (
    echo [ERROR] Restore failed. Check the log file for details.
    pause
    exit /b !EXIT_CODE!
)

echo [SUCCESS] Restore finished.
pause
exit /b 0
