param(
    [string]$EnvFile = ".env",
    [string]$ArtifactsDir = "dist"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent | Split-Path -Parent
$envLoader = Join-Path $root "scripts/azure/load_env.ps1"
if (Test-Path $envLoader) { & $envLoader -EnvFile $EnvFile | Out-Null }

$certKind = $env:CODE_SIGN_CERT_KIND
$certPath = $env:CODE_SIGN_CERT_PATH
$certPassword = $env:CODE_SIGN_CERT_PASSWORD

if (-not $certKind) { $certKind = "OV" }
if (-not $certPath) { throw "CODE_SIGN_CERT_PATH missing (set in .env)" }
if (-not (Test-Path $certPath)) {
    Write-Warning "Certificate path not found: $certPath (stub mode continues without actual signing)."
}

$manifest = @{
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    certificate_kind = $certKind
    certificate_path = $certPath
    artifacts_dir = $ArtifactsDir
    smartscreen_guidance_url = $env:SMARTSCREEN_GUIDANCE_URL
    mode = "stub"
    note = "Replace demo values in .env and integrate SignTool command for real signing."
} | ConvertTo-Json -Depth 5

$out = Join-Path $root "reports\code_sign_stub_manifest.json"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $out) | Out-Null
Set-Content -Path $out -Value $manifest -NoNewline
Write-Host "Stub code-sign manifest written to $out"