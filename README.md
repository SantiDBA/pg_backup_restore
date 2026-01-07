# PostgreSQL Backup and Restore Tools

A set of Python scripts to automate the backup and restoration of PostgreSQL databases. These tools facilitate compressed backups with retention policies and interactive restoration processes.

## Features

- **Automated Backup**: Create compressed (`.zip`) SQL dumps of your PostgreSQL databases.
- **Retention Policy**: Automatically clean up old backups based on a configurable number of days.
- **Scheduled Backups**: Easy setup for automatic backups on Windows using Task Scheduler.
- **Interactive Restore**: Safely restore databases from zip archives, with protections against accidental overwrites.
- **Logging**: Comprehensive logging for both backup and restore operations (`backup_postgres.log` and `restore_postgres.log`).
- **Dry Run**: Preview actions before they are executed.

## Prerequisites

Ensure you have the PostgreSQL client tools installed and available in your system's `PATH`:
- `pg_dump`
- `psql`
- `createdb`
- `dropdb`

The scripts are written in Python 3 and use standard libraries.

## Setup

1. Clone this repository or copy the scripts to your desired location.
2. Ensure the PostgreSQL binaries mentioned above are in your `PATH`.
3. (Optional) Set up a virtual environment, although no external Python dependencies are required.

---

## Backup Tool (`backup_postgres.py`)

This script dumps a PostgreSQL database to a `.sql` file, compresses it into a `.zip` archive, and manages the cleanup of older backups.

### Usage

```bash
python3 backup_postgres.py --host <HOST> --port <PORT> --database <DB_NAME> --username <USER> [OPTIONS]
```

### Arguments

| Argument | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `--host` | Yes | - | Database host address. |
| `--port` | Yes | - | Database port number. |
| `--database` | Yes | - | Name of the database to back up. |
| `--username` | Yes | - | Database username. |
| `--password` | No | Prompt | Database password. If omitted, you will be prompted securely. |
| `--backup-dir` | No | `.` | Directory where the `.zip` files will be stored. |
| `--retention-days`| No | `30` | Number of days to keep backups before deletion. |
| `--dry-run` | No | `False` | Show what would happen without creating or deleting any files. |

### Example

```bash
python3 backup_postgres.py --host localhost --port 5432 --database my_prod_db --username postgres --backup-dir ./backups --retention-days 7
```

---

## Restore Tool (`restore_postgres.py`)

This script restores a PostgreSQL database from a `.zip` archive created by the backup tool. 

> [!CAUTION]
> If the target database already exists, the script will ask for confirmation before dropping and re-creating it. Use the `--yes` flag with caution.

### Usage

```bash
python3 restore_postgres.py --host <HOST> --port <PORT> --target-database <DB_NAME> --username <USER> --zip-file <PATH_TO_ZIP> [OPTIONS]
```

### Arguments

| Argument | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `--host` | Yes | - | Database host address. |
| `--port` | Yes | - | Database port number. |
| `--target-database`| Yes | - | Name of the database to restore into. |
| `--username` | Yes | - | Database username. |
| `--password` | No | Prompt | Database password. |
| `--zip-file` | Yes | - | Path to the `.zip` backup archive. |
| `--yes` | No | `False` | Automatically confirm destructive actions (e.g., dropping an existing DB). |
| `--dry-run` | No | `False` | Show planned restoration steps without executing them. |

### Example

```bash
python3 restore_postgres.py --host localhost --port 5432 --target-database my_restored_db --username postgres --zip-file ./backups/my_prod_db_20260106_120000.zip
```

## Logging

- Backup logs are saved to `backup_postgres.log`.
- Restore logs are saved to `restore_postgres.log`.

These files contain timestamps, status messages, and error details for every run.

## Automated Scheduling (Windows)

To run the backup script automatically (e.g., daily), use Windows Task Scheduler. 

See the detailed guide: [SCHEDULING_WINDOWS.md](file:///Users/Santix/Documents/GitHub/pg_backup_restore/SCHEDULING_WINDOWS.md)

A template batch script is also provided: [run_backup_template.bat](file:///Users/Santix/Documents/GitHub/pg_backup_restore/run_backup_template.bat)
