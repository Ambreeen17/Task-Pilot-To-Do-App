@echo off
cls
echo.
echo ========================================
echo   Pushing to GitHub...
echo ========================================
echo.

cd /d "%~dp0"

echo Pushing all code to GitHub...
echo.

git remote set-url origin https://github.com/Ambreeen17/Task-Pilot-To-Do-App.git

git push -u origin master

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ✓ SUCCESS! Code pushed to GitHub
    echo ========================================
    echo.
    echo Repository: https://github.com/Ambreeen17/Task-Pilot-To-Do-App
    echo.
    pause
    exit /b 0
) else (
    echo.
    echo ========================================
    echo   ✗ Push failed!
    echo ========================================
    echo.
    echo Possible issues:
    echo 1. Token doesn't have 'repo' permissions
    echo 2. Token has expired
    echo 3. Repository already exists with different owner
    echo.
    echo Try this manually:
    echo 1. Go to: https://github.com/settings/tokens
    echo 2. Create new token with 'repo' scope
    echo 3. Run: git push -u origin master
    echo.
    pause
    exit /b 1
)
