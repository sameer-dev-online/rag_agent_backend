# Python Version Compatibility Fix

## Problem

Your pytest tests are failing with the error:
```
pydantic.v1.errors.ConfigError: unable to infer type for attribute "chroma_server_nofile"
```

**Root Cause**: Your virtual environment was created with **Python 3.14.2**, but **ChromaDB uses `pydantic.v1` which is not compatible with Python 3.14+**.

## Solution

Recreate your virtual environment with Python 3.12 or 3.13 (you have Python 3.12.3 available).

### Option 1: Automated Fix (Windows)

Run the provided batch script:

```cmd
fix_python_version.bat
```

This will:
1. Remove the old virtual environment
2. Create a new one with Python 3.12
3. Reinstall all dependencies
4. Everything should work after this

### Option 2: Manual Fix (Windows)

If you prefer to do it manually:

```cmd
# 1. Deactivate current venv (if activated)
deactivate

# 2. Delete the old virtual environment
rmdir /s /q venv

# 3. Create new venv with Python 3.12
py -3.12 -m venv venv

# 4. Activate the new venv
venv\Scripts\activate

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 7. Run pytest to verify
pytest
```

### Option 3: Using WSL/Linux Commands

If you're using WSL:

```bash
# 1. Remove old venv
rm -rf venv

# 2. Create new venv with Python 3.12
python3 -m venv venv

# 3. Activate
source venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 5. Run tests
pytest
```

## Verification

After recreating the venv, verify the Python version:

```cmd
# On Windows
venv\Scripts\python --version

# On WSL/Linux
./venv/bin/python --version
```

You should see `Python 3.12.x` or `Python 3.13.x` (not 3.14.x).

## Why This Happened

- ChromaDB depends on `pydantic.v1` (Pydantic version 1)
- Pydantic V1 core functionality isn't compatible with Python 3.14+
- The ChromaDB team will likely update this in the future
- Until then, we must use Python 3.13 or lower

## Documentation Updated

- `README.md` now specifies Python 3.10-3.13 requirement
- `TASK.md` tracks this fix
- This file documents the issue and solution

## Reference

ChromaDB warning message:
```
UserWarning: Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.
```
