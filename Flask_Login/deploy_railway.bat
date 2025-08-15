@echo off
echo ========================================
echo Railway Deployment Script
echo ========================================

REM Check if Railway CLI is installed
railway --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Railway CLI...
    npm install -g @railway/cli
    if %errorlevel% neq 0 (
        echo Failed to install Railway CLI. Please install manually.
        pause
        exit /b 1
    )
)

echo.
echo Logging into Railway...
railway login
if %errorlevel% neq 0 (
    echo Failed to login to Railway.
    pause
    exit /b 1
)

echo.
echo Linking project...
railway link
if %errorlevel% neq 0 (
    echo Failed to link project.
    pause
    exit /b 1
)

echo.
echo Setting environment variables...
echo Please set these environment variables in Railway dashboard:
echo - SECRET_KEY: A secure random string
echo - RECAPTCHA_SITE_KEY: Your reCAPTCHA key
echo.
echo Or use these commands:
echo railway variables set SECRET_KEY="your-secret-key"
echo railway variables set RECAPTCHA_SITE_KEY="your-recaptcha-key"

echo.
echo Deploying to Railway...
railway up

echo.
echo Deployment complete! Check status with: railway status
echo View logs with: railway logs
pause
