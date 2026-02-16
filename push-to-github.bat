@echo off
echo ========================================
echo TaskPilot - Push to GitHub
echo ========================================
echo.
echo This will push your code to GitHub.
echo You'll need to authenticate with your GitHub credentials.
echo.
pause

cd /d "%~dp0"

echo.
echo Pushing to GitHub...
echo.

git push -u origin master

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Successfully pushed to GitHub!
    echo ========================================
    echo.
    echo Your repo: https://github.com/Ambreeen17/Task-Pilot-To-Do-App
    echo.
) else (
    echo.
    echo ========================================
    echo Push failed. Please check:
    echo 1. You're authenticated with GitHub
    echo 2. You have access to Ambreeen17/Task-Pilot-To-Do-App
    echo 3. Your GitHub personal access token is valid
    echo ========================================
    echo.
    echo To authenticate, run:
    echo git config --global credential.helper store
    echo git push -u origin master
    echo.
)

pause
