# App launch + stub setup

## 1. Create `.env` from demo template
```powershell
Copy-Item .env.example .env
```

Then replace values in `.env` as needed.

## 2. Install dependencies
```powershell
python -m pip install -e .
```

## 3. Run app
```powershell
python -m pecan_crm
```

## 4. Optional stub artifact generation
```powershell
python scripts/ops/generate_access_inventory_stub.py --env-file .env
python scripts/ops/generate_restore_drill_stub.py --env-file .env
powershell -ExecutionPolicy Bypass -File scripts/ops/signing_stub.ps1 -EnvFile .env
```