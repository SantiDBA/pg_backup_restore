import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import sys
import os

class PgBackupRestoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Postgres Backup & Restore Manager")
        self.root.geometry("600x700")

        # Variables
        self.host_var = tk.StringVar(value="localhost")
        self.port_var = tk.IntVar(value=5432)
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # Backup Variables
        self.backup_db_var = tk.StringVar()
        self.backup_dir_var = tk.StringVar(value=os.getcwd())
        self.retention_var = tk.IntVar(value=30)
        self.backup_dry_run_var = tk.BooleanVar(value=False)

        # Restore Variables
        self.restore_target_db_var = tk.StringVar()
        self.restore_zip_var = tk.StringVar()
        self.restore_dry_run_var = tk.BooleanVar(value=True)
        self.restore_yes_var = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        # Common Connection Details
        conn_frame = ttk.LabelFrame(self.root, text="Connection Details", padding="10")
        conn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(conn_frame, textvariable=self.host_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        ttk.Entry(conn_frame, textvariable=self.port_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(conn_frame, text="Username:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(conn_frame, textvariable=self.username_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(conn_frame, text="Password:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        ttk.Entry(conn_frame, textvariable=self.password_var, show="*").grid(row=1, column=3, sticky="ew", padx=5, pady=2)
        
        conn_frame.columnconfigure(1, weight=1)

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Backup Tab
        self.backup_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.backup_frame, text="Backup")
        self.create_backup_widgets()

        # Restore Tab
        self.restore_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.restore_frame, text="Restore")
        self.create_restore_widgets()

        # Log Area
        log_frame = ttk.LabelFrame(self.root, text="Logs", padding="5")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text['yscrollcommand'] = scrollbar.set

    def create_backup_widgets(self):
        ttk.Label(self.backup_frame, text="Database Name:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(self.backup_frame, textvariable=self.backup_db_var).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(self.backup_frame, text="Backup Directory:").grid(row=1, column=0, sticky="w", pady=5)
        dir_frame = ttk.Frame(self.backup_frame)
        dir_frame.grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Entry(dir_frame, textvariable=self.backup_dir_var).pack(side="left", fill="x", expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_backup_dir).pack(side="left", padx=5)

        ttk.Label(self.backup_frame, text="Retention Days:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Spinbox(self.backup_frame, from_=1, to=3650, textvariable=self.retention_var, width=5).grid(row=2, column=1, sticky="w", pady=5)

        ttk.Checkbutton(self.backup_frame, text="Dry Run (Test only)", variable=self.backup_dry_run_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=10)

        ttk.Button(self.backup_frame, text="Start Backup", command=self.run_backup).grid(row=4, column=0, columnspan=2, pady=10)
        
        self.backup_frame.columnconfigure(1, weight=1)

    def create_restore_widgets(self):
        ttk.Label(self.restore_frame, text="Target Database:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(self.restore_frame, textvariable=self.restore_target_db_var).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(self.restore_frame, text="Backup Zip File:").grid(row=1, column=0, sticky="w", pady=5)
        file_frame = ttk.Frame(self.restore_frame)
        file_frame.grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Entry(file_frame, textvariable=self.restore_zip_var).pack(side="left", fill="x", expand=True)
        ttk.Button(file_frame, text="Browse", command=self.browse_zip_file).pack(side="left", padx=5)

        ttk.Checkbutton(self.restore_frame, text="Dry Run (Test only)", variable=self.restore_dry_run_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(self.restore_frame, text="Auto Confirm Replacement (--yes)", variable=self.restore_yes_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Button(self.restore_frame, text="Start Restore", command=self.run_restore).grid(row=4, column=0, columnspan=2, pady=10)
        
        self.restore_frame.columnconfigure(1, weight=1)

    def browse_backup_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.backup_dir_var.set(d)

    def browse_zip_file(self):
        f = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip"), ("All files", "*.*")])
        if f:
            self.restore_zip_var.set(f)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def run_command_thread(self, cmd):
        self.log(f"Running command: {' '.join(cmd)}")
        try:
            # We must pass subprocess.PIPE to capture output
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            if process.returncode == 0:
                self.log("SUCCESS")
                messagebox.showinfo("Success", "Operation completed successfully!")
            else:
                self.log(f"FAILED with return code {process.returncode}")
                messagebox.showerror("Error", "Operation failed. Check logs.")
        except Exception as e:
            self.log(f"EXCEPTION: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

    def run_backup(self):
        host = self.host_var.get()
        port = str(self.port_var.get())
        user = self.username_var.get()
        password = self.password_var.get()
        db = self.backup_db_var.get()
        directory = self.backup_dir_var.get()
        retention = str(self.retention_var.get())

        if not all([host, port, user, db]):
            messagebox.showwarning("Validation", "Please fill in all required fields.")
            return

        cmd = [
            sys.executable, "backup_postgres.py",
            "--host", host,
            "--port", port,
            "--username", user,
            "--password", password,
            "--database", db,
            "--backup-dir", directory,
            "--retention-days", retention
        ]

        if self.backup_dry_run_var.get():
            cmd.append("--dry-run")

        threading.Thread(target=self.run_command_thread, args=(cmd,), daemon=True).start()

    def run_restore(self):
        host = self.host_var.get()
        port = str(self.port_var.get())
        user = self.username_var.get()
        password = self.password_var.get()
        db = self.restore_target_db_var.get()
        zip_file = self.restore_zip_var.get()

        if not all([host, port, user, db, zip_file]):
            messagebox.showwarning("Validation", "Please fill in all required fields.")
            return

        cmd = [
            sys.executable, "restore_postgres.py",
            "--host", host,
            "--port", port,
            "--username", user,
            "--password", password,
            "--target-database", db,
            "--zip-file", zip_file
        ]

        if self.restore_dry_run_var.get():
            cmd.append("--dry-run")
        
        if self.restore_yes_var.get():
            cmd.append("--yes")

        threading.Thread(target=self.run_command_thread, args=(cmd,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = PgBackupRestoreApp(root)
    root.mainloop()
