param(
    [string]$AdminEmail = "admin@offerpilot.example.com"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $root ".env"

if (-not (Test-Path -LiteralPath $envPath)) {
    $databasePassword = [Convert]::ToBase64String(
        [Security.Cryptography.RandomNumberGenerator]::GetBytes(24)
    ).Replace("/", "_").Replace("+", "-").TrimEnd("=")
    $secretKey = [Convert]::ToBase64String(
        [Security.Cryptography.RandomNumberGenerator]::GetBytes(48)
    ).Replace("/", "_").Replace("+", "-").TrimEnd("=")
    $content = @"
POSTGRES_DB=offerpilot
POSTGRES_USER=offerpilot
POSTGRES_PASSWORD=$databasePassword
DATABASE_URL=postgresql+psycopg://offerpilot:$databasePassword@localhost:5432/offerpilot
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$secretKey
CORS_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
UPLOAD_DIR=data/uploads
MAX_UPLOAD_BYTES=10485760
MAX_IMPORT_BYTES=5242880
ADMIN_EMAILS=$($AdminEmail.ToLowerInvariant())
"@
    Set-Content -LiteralPath $envPath -Value $content -Encoding utf8
    Write-Host "Created local .env with generated secrets."
}

Push-Location $root
try {
    docker compose up --build -d --wait
    docker compose ps
}
finally {
    Pop-Location
}

Write-Host "OfferPilot AI is running at http://localhost:3000"
Write-Host "Register $AdminEmail to receive local data governance access."
