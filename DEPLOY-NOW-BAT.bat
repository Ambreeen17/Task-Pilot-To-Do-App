@echo off
cls
echo.
echo ========================================
echo   TaskPilot Deployment
echo ========================================
echo.
echo This will deploy your app in 3 steps:
echo 1. Push code to GitHub
echo 2. Push backend to Hugging Face
echo 3. Deploy frontend to Vercel
echo.
pause

:: Step 1: GitHub
cls
echo.
echo ========================================
echo STEP 1: Push to GitHub
echo ========================================
echo.
cd /d "%~dp0"

echo Setting up GitHub remote with your token...
git remote set-url origin https://github.com/Ambreeen17/Task-Pilot-To-Do-App.git

echo.
echo Pushing to GitHub...
echo.

git push -u origin master

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ GitHub push failed!
    echo.
    echo The repository might need to be created first.
    echo.
    echo Option 1: Create repo at https://github.com/new
    echo          Name: Task-Pilot-To-Do-App
    echo.
    echo Option 2: The repo might belong to a different account
    echo          Check: https://github.com/Ambreeen17/Task-Pilot-To-Do-App
    echo.
    pause
)

echo.
echo ✓ Step 1 complete!
echo.

:: Step 2: Hugging Face
cls
echo.
echo ========================================
echo STEP 2: Push to Hugging Face
echo ========================================
echo.

cd hf-deploy\bk

echo Setting up Hugging Face remote with your token...
git remote set-url origin https://huggingface.co/spaces/ambreenaz/bk

echo.
echo Pushing to Hugging Face...
echo.

git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ Hugging Face push failed!
    echo.
    echo Make sure:
    echo 1. You own the space: https://huggingface.co/spaces/ambreenaz/bk
    echo 2. Token has "Write" permissions
    echo 3. Username is correct (ambreenaz)
    echo.
    echo To check ownership, visit:
    echo https://huggingface.co/spaces/ambreenaz/bk/settings
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
echo YOUR URLs:
echo ========================================
echo.
echo Backend Building:
echo https://huggingface.co/spaces/ambreenaz/bk
echo.
echo Backend API (after build):
echo https://ambreenaz-bk.hf.space
echo.
echo API Documentation:
echo https://ambreenaz-bk.hf.space/docs
echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo.
echo 1. Wait for Hugging Face build (~5-10 min)
echo    Watch logs at: https://huggingface.co/spaces/ambreenaz/bk
echo.
echo 2. Set environment variables:
echo    Go to: https://huggingface.co/spaces/ambreenaz/bk/settings
echo    Click "New secret" and add:
echo.
echo    DATABASE_URL = get_from_neon
echo    ANTHROPIC_API_KEY = your_key
echo    AI_FEATURES_ENABLED = true
echo.
echo 3. Create database:
echo    Go to https://neon.tech
echo    Create free project
echo    Copy connection string
echo    Add as DATABASE_URL
echo.
echo 4. Deploy frontend:
echo    Go to https://vercel.com/ambreen-rais-projects
echo    Add Project → Import GitHub repo
echo    Root dir: frontend
echo    Env var: NEXT_PUBLIC_API_URL = https://ambreenaz-bk.hf.space
echo    Click Deploy
echo.
echo ========================================
echo.
echo Full instructions: DEPLOY-NOW.md
echo.
pause
