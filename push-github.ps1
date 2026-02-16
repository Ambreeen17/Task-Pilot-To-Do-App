# Push to GitHub Script
# Run this in PowerShell

Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "  Pushing TaskPilot to GitHub"  -ForegroundColor Cyan
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""

# Set working directory
Set-Location "C:\Users\User\Desktop\Task-Pilot-To-Do-App-005-adaptive-intelligence"

# Configure git credential helper
Write-Host "Configuring git credentials..." -ForegroundColor Yellow
git config --global credential.helper store

# Set remote URL
Write-Host "Setting remote URL..." -ForegroundColor Yellow
git remote set-url origin https://github.com/Ambreeen17/Task-Pilot-To-Do-App.git

# Configure credentials (will prompt for login)
Write-Host "You will be prompted for GitHub credentials..." -ForegroundColor Yellow

Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Green
Write-Host ""

git push -u origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================"  -ForegroundColor Green
    Write-Host "  ✓ SUCCESS!"  -ForegroundColor Green
    Write-Host "========================================"  -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository: https://github.com/Ambreeen17/Task-Pilot-To-Do-App" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================"  -ForegroundColor Red
    Write-Host "  ✗ Push failed!"  -ForegroundColor Red
    Write-Host "========================================"  -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "1. Token doesn't have 'repo' scope" -ForegroundColor Yellow
    Write-Host "2. Repository belongs to different account" -ForegroundColor Yellow
    Write-Host "3. Token has expired" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Check your token at:" -ForegroundColor Cyan
    Write-Host "https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
