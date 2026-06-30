# Start Cloudflare Tunnel for local Ollama.
# Usage:
#   .\scripts\start-ollama-tunnel.ps1              # named tunnel (stable URL)
#   .\scripts\start-ollama-tunnel.ps1 -Quick         # random trycloudflare.com URL

param(
    [switch]$Quick
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$configPath = Join-Path $repoRoot "scripts\cloudflared-config.yml"

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host "cloudflared not found. Install with:" -ForegroundColor Yellow
    Write-Host "  winget install Cloudflare.cloudflared"
    Write-Host "See docs/CLOUDFLARE_TUNNEL.md for full setup."
    exit 1
}

# Confirm Ollama is up
try {
    $null = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    Write-Host "Ollama is running on localhost:11434" -ForegroundColor Green
} catch {
    Write-Host "Ollama is not reachable at localhost:11434. Start Ollama first." -ForegroundColor Red
    exit 1
}

if ($Quick) {
    Write-Host "Starting quick tunnel (URL changes each run)..." -ForegroundColor Cyan
    cloudflared tunnel --url http://localhost:11434
    exit $LASTEXITCODE
}

if (-not (Test-Path $configPath)) {
    Write-Host "Missing $configPath" -ForegroundColor Yellow
    Write-Host "Copy scripts/cloudflared-config.example.yml and follow docs/CLOUDFLARE_TUNNEL.md"
    exit 1
}

Write-Host "Starting named tunnel from $configPath ..." -ForegroundColor Cyan
cloudflared tunnel --config $configPath run ollama
