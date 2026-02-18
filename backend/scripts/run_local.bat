@echo off
setlocal EnableExtensions

REM Run from backend\ regardless of current working directory
cd /d %~dp0\..

REM Django 6.x requires Python 3.12+
python -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" >nul
if errorlevel 1 (
  for /f "delims=" %%v in ('python -c "import sys; print(sys.version.split()[0])"') do set PYVER=%%v
  echo Python 3.12+ required for Django 6.x. Your version: %PYVER%
  exit /b 1
)

if not exist .venv\Scripts\python.exe (
  python -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 127.0.0.1:8000

endlocal