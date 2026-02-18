$ErrorActionPreference = "Stop"

# Run from backend/ regardless of current working dir
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..

# Django 6.x requires Python 3.12+
python -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" | Out-Null
if ($LASTEXITCODE -ne 0) {
  $ver = python -c "import sys; print(sys.version.split()[0])"
  Write-Host "Python 3.12+ required for Django 6.x. Your version: $ver"
  exit 1
}

if (!(Test-Path .venv\Scripts\python.exe)) {
  python -m venv .venv
}

. .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 127.0.0.1:8000