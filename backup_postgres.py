import argparse
import subprocess
import os
import datetime
import zipfile
import sys
import logging
import time
import glob
import shutil
import getpass

# Logging is configured in the main block or by the importing application



def cleanup_old_backups(database, retention_days=30, backup_dir="."):
    """Deletes backup files older than retention_days in backup_dir."""
    logging.info(f"Starting cleanup of backups older than {retention_days} days for database '{database}' in '{backup_dir}'...")
    now = time.time()
    cutoff = now - (retention_days * 86400)

    pattern = os.path.join(backup_dir, f"{database}_*.zip")
    files = glob.glob(pattern)

    for f in files:
        try:
            mtime = os.path.getmtime(f)
            if mtime < cutoff:
                os.remove(f)
                logging.info(f"Deleted old backup: {f}")
                print(f"Deleted old backup: {f}")
        except Exception as e:
            logging.error(f"Error deleting old backup {f}: {e}")
            print(f"Error deleting old backup {f}: {e}")


def backup_postgres(host, port, database, username, password, backup_dir=".", retention_days=30, dry_run=False, bin_dir=None):
    """Backs up a PostgreSQL database to a zipped archive."""
    logging.info(f"Starting backup for database '{database}' on {host}:{port}")

    # Resolve pg_dump path
    pg_dump_path = "pg_dump"
    if bin_dir:
        pg_dump_path = os.path.join(bin_dir, "pg_dump")
        if sys.platform == "win32" and not pg_dump_path.lower().endswith(".exe"):
            pg_dump_path += ".exe"

    if shutil.which(pg_dump_path) is None:
        msg = f"'{pg_dump_path}' not found. Please install PostgreSQL tools or check the bin path."
        print(msg)
        logging.error(msg)
        raise EnvironmentError(msg)

    # Ensure backup dir exists
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_filename = f"{database}_{timestamp}.sql"
    zip_filename = f"{database}_{timestamp}.zip"
    dump_path = os.path.join(backup_dir, dump_filename)
    zip_path = os.path.join(backup_dir, zip_filename)

    env = os.environ.copy()
    env['PGPASSWORD'] = password

    pg_dump_cmd = [
        pg_dump_path,
        '-h', host,
        '-p', str(port),
        '-U', username,
        '-d', database,
        '-f', dump_path
    ]

    print(f"Starting backup for database '{database}' on {host}:{port}...")
    try:
        if dry_run:
            print("[DRY-RUN] Would run:", ' '.join(pg_dump_cmd))
            print("[DRY-RUN] Skipping actual dump due to dry-run")
            print(f"[DRY-RUN] Would create dump at: {dump_path}")
            print(f"[DRY-RUN] Would create zip at: {zip_path}")
            print(f"[DRY-RUN] Would cleanup backups older than {retention_days} days in {backup_dir}")
            return
        subprocess.run(pg_dump_cmd, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Database dump created: {dump_path}")
        logging.info(f"Database dump created: {dump_path}")

        # Compress to zip
        print(f"Compressing to {zip_path}...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(dump_path, arcname=os.path.basename(dump_path))

        print(f"Backup saved successfully: {zip_path}")
        logging.info(f"Backup saved successfully: {zip_path}")

        # Cleanup old backups after success
        cleanup_old_backups(database, retention_days=retention_days, backup_dir=backup_dir)

    except subprocess.CalledProcessError as e:
        msg = f"Error running pg_dump: {e}"
        print(msg)
        logging.error(msg)
        if os.path.exists(zip_path):
            os.remove(zip_path)
            logging.info(f"Cleaned up incomplete zip file: {zip_path}")
        raise
    except Exception as e:
        msg = f"An unexpected error occurred: {e}"
        print(msg)
        logging.error(msg)
        if os.path.exists(zip_path):
            os.remove(zip_path)
            logging.info(f"Cleaned up incomplete zip file: {zip_path}")
        raise
    finally:
        if os.path.exists(dump_path):
            os.remove(dump_path)
            print(f"Cleaned up temporary file: {dump_path}")
            logging.info(f"Cleaned up temporary file: {dump_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup a PostgreSQL database to a ZIP file.")
    parser.add_argument("--host", required=True, help="Database host")
    parser.add_argument("--port", type=int, required=True, help="Database port")
    parser.add_argument("--database", required=True, help="Database name")
    parser.add_argument("--username", required=True, help="Database username")
    parser.add_argument("--password", required=False, help="Database password (will prompt if omitted)")
    parser.add_argument("--backup-dir", default='.', help="Directory to store backups")
    parser.add_argument("--retention-days", type=int, default=30, help="Retention days for backups")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes)" )

    parser.add_argument("--bin-dir", help="Directory containing PostgreSQL binaries (pg_dump)")

    args = parser.parse_args()

    # Password handling: prompt if omitted
    if args.password:
        pwd = args.password
    else:
        pwd = getpass.getpass("Database password: ")

    # Configure logging for CLI usage
    logging.basicConfig(
        filename='backup_postgres.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    backup_postgres(args.host, args.port, args.database, args.username, pwd, backup_dir=args.backup_dir, retention_days=args.retention_days, dry_run=args.dry_run, bin_dir=args.bin_dir)
