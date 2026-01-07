# Scheduling Backups on Windows (Task Scheduler)

To run your backups automatically at specific intervals (like a daily backup), you can use the built-in **Windows Task Scheduler**.

## Step 1: Create a Batch File

It is easier to schedule a `.bat` file that sets the environment and runs the Python script. 

1.  Create a file named `run_backup.bat` in your project folder.
2.  Paste the following template and **edit the paths/credentials** to match your setup:

```batch
@echo off
:: --- SETTINGS ---
set PYTHON_EXE=C:\Path\To\Python\python.exe
set SCRIPT_PATH=C:\Path\To\pg_backup_restore\backup_postgres.py
set BACKUP_DIR=C:\Backups

:: DB SETTINGS
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=your_database
set DB_USER=postgres
set DB_PASSWORD=your_password

:: --- EXECUTION ---
%PYTHON_EXE% %SCRIPT_PATH% ^
    --host %DB_HOST% ^
    --port %DB_PORT% ^
    --database %DB_NAME% ^
    --username %DB_USER% ^
    --password %DB_PASSWORD% ^
    --backup-dir %BACKUP_DIR% ^
    --retention-days 30

exit /b %ERRORLEVEL%
```

## Step 2: Open Task Scheduler

1.  Press `Win + R`, type `taskschd.msc`, and hit Enter.
2.  Click **Create Basic Task...** in the right-hand panel.

## Step 3: Configure the Task

1.  **Name**: e.g., "Postgres Daily Backup".
2.  **Trigger**: Select **Daily** (or your preferred frequency).
3.  **Time**: Set the time (e.g., 02:00 AM).
4.  **Action**: Select **Start a program**.
5.  **Program/script**: Click **Browse** and select your `run_backup.bat` file.
6.  **Start in (optional)**: Paste the directory path where your project files are located (e.g., `C:\Path\To\pg_backup_restore`).
7.  **Finish**: Click Finish.

## Step 4: Refine Settings (Important)

1.  Find your task in the "Task Scheduler Library".
2.  Right-click it and select **Properties**.
3.  On the **General** tab, select **Run whether user is logged on or not**.
4.  Select **Run with highest privileges** (to ensure it has write access to the backup folder).
5.  On the **Settings** tab, ensure "Allow task to be run on demand" is checked.

## Step 5: Test It

1.  Right-click the task in the list and select **Run**.
2.  Check your `backup_postgres.log` and the backup directory to confirm it worked!
