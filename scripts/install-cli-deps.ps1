# Install Super-Agents CLI dependencies (Windows PowerShell)

Write-Host "Installing Super-Agents CLI Dependencies..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "Error: Python not found. Please install Python 3.7 or later." -ForegroundColor Red
    exit 1
}

# Get Python version
$pythonVersion = & python --version
Write-Host "Using: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Install requirements
Write-Host "Installing dependencies from requirements-cli.txt..." -ForegroundColor Cyan
& pip install -r requirements-cli.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Installation complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run:" -ForegroundColor Cyan
    Write-Host "  python cli.py init" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ Installation failed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Try manual installation:" -ForegroundColor Yellow
    Write-Host "  pip install click rich questionary tabulate" -ForegroundColor White
    exit 1
}
