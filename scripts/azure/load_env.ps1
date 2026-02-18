param(
    [string]$EnvFile = ".env",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $EnvFile)) {
    Write-Host "No .env file at $EnvFile"
    return
}

Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
        return
    }

    $parts = $line.Split("=", 2)
    $key = $parts[0].Trim()
    $value = $parts[1].Trim().Trim("`\"").Trim("'")

    if ($Force -or -not (Get-Item "Env:$key" -ErrorAction SilentlyContinue)) {
        Set-Item -Path "Env:$key" -Value $value
    }
}

Write-Host "Loaded environment variables from $EnvFile"