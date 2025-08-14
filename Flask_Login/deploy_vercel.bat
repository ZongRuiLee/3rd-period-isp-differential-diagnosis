@echo off
echo 🚀 Deploying Flask App to Vercel
echo ==================================

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Vercel CLI not found. Installing...
    npm install -g vercel
)

REM Check if user is logged in
vercel whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 Please login to Vercel...
    vercel login
)

echo 📁 Preparing deployment...

REM Create .vercelignore if it doesn't exist
if not exist .vercelignore (
    echo 📝 Creating .vercelignore...
    (
        echo venv/
        echo __pycache__/
        echo *.pyc
        echo *.pyo
        echo *.pyd
        echo .Python
        echo env/
        echo pip-log.txt
        echo pip-delete-this-directory.txt
        echo .tox/
        echo .coverage
        echo .coverage.*
        echo .cache
        echo nosetests.xml
        echo coverage.xml
        echo *.cover
        echo *.log
        echo .git/
        echo .mypy_cache/
        echo .pytest_cache/
        echo .hypothesis/
        echo .idea/
        echo *.joblib
        echo *.csv
        echo *.db
    ) > .vercelignore
)

echo 🚀 Starting deployment...
echo Choose deployment option:
echo 1. Full version (requires external ML models and database)
echo 2. Simple version (demo only, works immediately)

set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo 📦 Deploying full version...
    echo ⚠️  Note: You'll need to set up external ML models and database
    vercel --prod
) else if "%choice%"=="2" (
    echo 📦 Deploying simple version...
    echo 📝 Updating vercel.json for simple deployment...
    
    REM Update vercel.json for simple deployment
    (
        echo {
        echo   "version": 2,
        echo   "builds": [
        echo     {
        echo       "src": "api/simple_index.py",
        echo       "use": "@vercel/python"
        echo     }
        echo   ],
        echo   "routes": [
        echo     {
        echo       "src": "/(.*)",
        echo       "dest": "/api/simple_index.py"
        echo     }
        echo   ],
        echo   "functions": {
        echo     "api/simple_index.py": {
        echo       "maxDuration": 30
        echo     }
        echo   }
        echo }
    ) > vercel.json
    
    vercel --prod
) else (
    echo ❌ Invalid choice. Exiting.
    exit /b 1
)

echo ✅ Deployment complete!
echo 🌐 Your app should be available at the URL shown above
echo.
echo 📋 Next steps:
echo 1. Set environment variables in Vercel dashboard
echo 2. Test your application
echo 3. Set up external services if using full version

pause 