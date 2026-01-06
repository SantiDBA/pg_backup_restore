import argparse
import os
import zipfile
import sys
import logging
import shutil
import getpass
import subprocess

# Configure logging
logging.basicConfig(
    filename='restore_postgres.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def restore_postgres(host, port, target_database, username, password, zip_file, auto_confirm=False, dry_run=False):
    """Restores a PostgreSQL database from a ZIP file."""
    logging.info(f"Starting restore for database '{target_database}' from {zip_file}")

    # Dry-run: show planned steps without performing actions
    if dry_run:
        print("[DRY-RUN] Restore would perform with:")
        print(f"  host={host}, port={port}, target_database={target_database}, zip_file={zip_file}")
        print("  Would unzip the archive, locate SQL, create/replace database, and run psql to restore.")
        return

    # Preflight: ensure required binaries exist
    if shutil.which("psql") is None or shutil.which("createdb") is None or shutil.which("dropdb") is None:
        msg = "Required PostgreSQL commands (psql/createdb/dropdb) not found in PATH."
        print(msg)
        logging.error(msg)
        raise EnvironmentError(msg)

    # 1. Unzip the file
    print(f"Unzipping {zip_file}...")
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            sql_file = None
            for f in file_list:
                if f.endswith('.sql'):
                    sql_file = f
                    break

            if not sql_file:
                msg = "Error: No .sql file found in the zip archive."
                print(msg)
                logging.error(msg)
                raise ValueError(msg)

            zip_ref.extract(sql_file)
            sql_file_path = sql_file
            print(f"Extracted: {sql_file_path}")
            logging.info(f"Extracted: {sql_file_path}")
    except zipfile.BadZipFile:
        msg = "Error: Invalid zip file."
        print(msg)
        logging.error(msg)
        raise
    except Exception as e:
        msg = f"Error extracting zip: {e}"
        print(msg)
        logging.error(msg)
        raise

    # Set password in environment variable for all libpq commands
    env = os.environ.copy()
    env['PGPASSWORD'] = password

    # 2. Check/Create Database
    print(f"Checking/Creating database '{target_database}'...")

    createdb_cmd = [
        'createdb',
        '-h', host,
        '-p', str(port),
        '-U', username,
        target_database
    ]

    try:
        # Try to create the database.
        subprocess.run(createdb_cmd, env=env, check=True, capture_output=True)
        print(f"Database '{target_database}' created.")
        logging.info(f"Database '{target_database}' created.")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ""
        if "already exists" in stderr:
            print(f"Database '{target_database}' already exists.")
            logging.info(f"Database '{target_database}' already exists.")

            # Interactive confirmation or auto-confirm
            if auto_confirm:
                print(f"Replacing database '{target_database}' as --yes was provided.")
                logging.info(f"Auto-replacing database '{target_database}' due to --yes.")

                dropdb_cmd = [
                    'dropdb',
                    '-h', host,
                    '-p', str(port),
                    '-U', username,
                    target_database
                ]

                def kill_sessions():
                    kill_cmd = [
                        'psql',
                        '-h', host,
                        '-p', str(port),
                        '-U', username,
                        '-d', 'postgres',
                        '-c', f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{target_database}' AND pid <> pg_backend_pid();"
                    ]
                    subprocess.run(kill_cmd, env=env, check=True, capture_output=True)

                try:
                    subprocess.run(dropdb_cmd, env=env, check=True, capture_output=True)
                    print(f"Database '{target_database}' dropped.")
                    logging.info(f"Database '{target_database}' dropped.")
                except subprocess.CalledProcessError as e2:
                    stderr = e2.stderr.decode() if e2.stderr else ""
                    if "accessed by other users" in stderr:
                        print(f"Database '{target_database}' is being accessed by other users.")
                        log_msg = "Active sessions detected. Cannot drop."
                        print(log_msg)
                        print(log_msg)
                        logging.info(log_msg)
                        raise RuntimeError(log_msg)
                    else:
                        msg = f"Error dropping database: {stderr}"
                        print(msg)
                        logging.error(msg)
                        raise RuntimeError(msg)

                # Re-create
                try:
                    subprocess.run(createdb_cmd, env=env, check=True, capture_output=True)
                    print(f"Database '{target_database}' re-created.")
                    logging.info(f"Database '{target_database}' re-created.")
                except subprocess.CalledProcessError as e3:
                    msg = f"Error re-creating database: {e3.stderr.decode() if e3.stderr else ''}"
                    print(msg)
                    logging.error(msg)
                    raise RuntimeError(msg)
            else:
                msg = "Restore cancelled by user."
                print(msg)
                logging.info(msg)
                return
        else:
            msg = f"Error creating database: {stderr}"
            print(msg)
            logging.error(msg)
            raise RuntimeError(msg)

    # 3. Restore using psql
    print(f"Restoring data into '{target_database}'...")

    psql_cmd = [
        'psql',
        '-h', host,
        '-p', str(port),
        '-U', username,
        '-d', target_database,
        '-f', sql_file_path
    ]

    try:
        subprocess.run(psql_cmd, env=env, check=True)
        print("Restore completed successfully.")
        logging.info("Restore completed successfully.")
    except subprocess.CalledProcessError as e:
        msg = f"Error running psql: {e}"
        print(msg)
        logging.error(msg)
        raise
    finally:
        # 4. Cleanup
        if os.path.exists(sql_file_path):
            os.remove(sql_file_path)
            print(f"Cleaned up temporary file: {sql_file_path}")
            logging.info(f"Cleaned up temporary file: {sql_file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore a PostgreSQL database from a ZIP file.")
    parser.add_argument("--host", required=True, help="Database host")
    parser.add_argument("--port", type=int, required=True, help="Database port")
    parser.add_argument("--target-database", required=True, help="Target database name")
    parser.add_argument("--username", required=True, help="Database username")
    parser.add_argument("--password", required=False, help="Database password (will prompt if omitted)")
    parser.add_argument("--zip-file", required=True, help="Path to the .zip backup file")
    parser.add_argument("--yes", action="store_true", help="Automatically confirm destructive prompts")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes)")

    args = parser.parse_args()

    password = args.password if args.password is not None else getpass.getpass("Database password: ")

    restore_postgres(
        args.host,
        args.port,
        args.target_database,
        args.username,
        password,
        args.zip_file,
        auto_confirm=args.yes,
        dry_run=args.dry_run,
    )
