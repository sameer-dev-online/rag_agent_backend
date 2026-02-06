@echo off
REM Fix Python version compatibility issue
REM ChromaDB requires Python 3.13 or lower

echo Removing old virtual environment...
rmdir /s /q venv

echo Creating new virtual environment with Python 3.12...
py -3.12 -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo.
echo Done! Virtual environment recreated with Python 3.12.
echo You can now run: pytest
