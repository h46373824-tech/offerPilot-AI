param(
    [Parameter(Mandatory = $true)]
    [string]$Email
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    docker compose exec -T backend python -m app.db.promote_admin $Email
}
finally {
    Pop-Location
}
