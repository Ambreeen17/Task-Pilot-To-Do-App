@echo off
echo ========================================
echo Push TaskPilot Backend to Hugging Face
echo ========================================
echo.
echo This will deploy your backend to Hugging Face Spaces.
echo.
pause

cd /d "%~dp0\hf-deploy\bk"

echo.
echo Logging in to Hugging Face...
echo.

REM Login to Hugging Face
huggingface-cli login

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo Hugging Face CLI not found!
    echo ========================================
    echo.
    echo Please install it first:
    echo pip install huggingface_hub
    echo.
    echo Or use Git with your HF token:
    echo 1. Go to: https://huggingface.co/settings/tokens
    echo 2. Create a token with "Write" permissions
    echo 3. Run: git push https://USERNAME:TOKEN@huggingface.co/spaces/ambreenaz/bk main
    echo.
    pause
    exit /b 1
)

echo.
echo Pushing to Hugging Face...
echo.

git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Successfully deployed to Hugging Face!
    echo ========================================
    echo.
    echo Your backend will be built at:
    echo https://huggingface.co/spaces/ambreenaz/bk
    echo.
    echo Watch the build progress at:
    echo https://huggingface.co/spaces/ambreenaz/bk/tree/main
    echo.
    echo Next steps:
    echo 1. Set environment variables in Space settings
    echo 2. Create database on Neon
    echo 3. Run migrations
    echo.
    echo See DEPLOY-YOUR-HF.md for detailed instructions
    echo.
) else (
    echo.
    echo ========================================
    echo Push failed!
    echo ========================================
    echo.
    echo Try manually with your token:
    echo git push https://ambreenaz:YOUR_TOKEN@huggingface.co/spaces/ambreenaz/bk main
    echo.
)

pause
