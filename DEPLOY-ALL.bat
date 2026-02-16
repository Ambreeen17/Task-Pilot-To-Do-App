@echo off
cls
echo.
echo ========================================
echo   TaskPilot - One-Click Deployment
echo ========================================
echo.
echo This will deploy your entire app:
echo 1. Push code to GitHub
echo 2. Push backend to Hugging Face
echo.
echo You'll need:
echo - GitHub Personal Access Token
echo - Hugging Face Access Token
echo.
pause

cls
echo.
echo ========================================
echo STEP 1: Push to GitHub
echo ========================================
echo.
cd /d "%~dp0"

echo Pushing to GitHub...
echo.

git push -u origin master

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ GitHub push successful!
    echo.
) else (
    echo.
    echo ✗ GitHub push failed!
    echo.
    echo Please create a Personal Access Token:
    echo https://github.com/settings/tokens/new?scopes=repo
    echo.
    echo Then run: git push -u origin master
    echo.
    pause
    exit /b 1
)

cls
echo.
echo ========================================
echo STEP 2: Push to Hugging Face
echo ========================================
echo.
echo Pushing backend to Hugging Face...
echo.

cd hf-deploy\bk

git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Hugging Face push successful!
    echo.
) else (
    echo.
    echo ✗ Hugging Face push failed!
    echo.
    echo Get your token: https://huggingface.co/settings/tokens
    echo.
    echo Then run:
    echo cd hf-deploy\bk
    echo git push https://ambreenaz:YOUR_TOKEN@huggingface.co/spaces/ambreenaz/bk main
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

cls
echo.
echo ========================================
echo   DEPLOYMENT SUCCESSFUL!
echo ========================================
echo.
echo ✓ Code pushed to GitHub
echo ✓ Backend pushed to Hugging Face
echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo.
echo 1. Backend is building at:
echo    https://huggingface.co/spaces/ambreenaz/bk
echo.
echo 2. Set environment variables:
echo    https://huggingface.co/spaces/ambreenaz/bk/settings
echo.
echo 3. Create database on Neon:
echo    https://neon.tech
echo.
echo 4. Run migrations (after build completes)
echo.
echo 5. Deploy frontend on Vercel:
echo    https://vercel.com/ambreen-rais-projects
echo.
echo ========================================
echo.
echo See DEPLOY-NOW.md for detailed instructions
echo.
pause
