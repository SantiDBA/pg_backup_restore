# Building for Windows

Since you are on macOS, please note: **PyInstaller CANNOT cross-compile**. You cannot create a Windows `.exe` file directly on macOS.

You have two main options:
1.  **Build on Windows**: Move your source code to the Windows machine and run PyInstaller there (as described below).
2.  **Use GitHub Actions**: Let GitHub build the `.exe` for you automatically (recommend if you don't want to install Python on the target machine).

---

## Option 1: Build on a Windows Machine (Fastest if you have Python installed there)

1.  **Copy Files**: Copy `pg_backup_restore_gui.py`, `backup_postgres.py`, and `restore_postgres.py` to your Windows machine.
2.  **Install Python**: Ensure Python is installed on Windows.
3.  **Install Libraries**:
    ```powershell
    pip install pyinstaller
    ```
4.  **Run Build**:
    ```powershell
    pyinstaller --noconsole --onefile --name "PostgresManager" pg_backup_restore_gui.py
    ```
5.  **Result**: The file will be in `dist\PostgresManager.exe`.

---

## Option 2: Use GitHub Actions (No Windows Python setup needed)

If you host this code on GitHub, you can use a workflow to build the .exe automatically.

1.  Create a file in your project: `.github/workflows/build_windows.yml`
2.  Paste this content:

```yaml
name: Build Windows Exe

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyinstaller
        
    - name: Build with PyInstaller
      run: |
        pyinstaller --noconsole --onefile --name "PostgresManager" pg_backup_restore_gui.py
        
    - name: Upload Artifact
      uses: actions/upload-artifact@v4
      with:
        name: PostgresManager-Windows
        path: dist/PostgresManager.exe
```

3.  Push your code to GitHub.
4.  Go to the "Actions" tab in your repository.
5.  Download the "PostgresManager-Windows" artifact once the run completes.

---

## Distribution Notes
- **Scripts**: Remember that `backup_postgres.py` and `restore_postgres.py` must be in the same folder as the `.exe` when you run it, unless you modified the .spec file to bundle them.
- **PostgreSQL Tools**: The machine running the app **MUST** have standard PostgreSQL client tools (`pg_dump`, `psql`, etc.) installed and in the system PATH. This app relies on them.
