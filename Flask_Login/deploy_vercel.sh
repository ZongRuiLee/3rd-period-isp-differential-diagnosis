#!/bin/bash

echo "🚀 Deploying Flask App to Vercel"
echo "=================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel..."
    vercel login
fi

echo "📁 Preparing deployment..."

# Create .vercelignore if it doesn't exist
if [ ! -f .vercelignore ]; then
    echo "📝 Creating .vercelignore..."
    cat > .vercelignore << EOF
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/
.idea/
*.joblib
*.csv
*.db
EOF
fi

echo "🚀 Starting deployment..."
echo "Choose deployment option:"
echo "1. Full version (requires external ML models and database)"
echo "2. Simple version (demo only, works immediately)"

read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "📦 Deploying full version..."
        echo "⚠️  Note: You'll need to set up external ML models and database"
        vercel --prod
        ;;
    2)
        echo "📦 Deploying simple version..."
        echo "📝 Updating vercel.json for simple deployment..."
        
        # Update vercel.json for simple deployment
        cat > vercel.json << EOF
{
  "version": 2,
  "builds": [
    {
      "src": "api/simple_index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/simple_index.py"
    }
  ],
  "functions": {
    "api/simple_index.py": {
      "maxDuration": 30
    }
  }
}
EOF
        
        vercel --prod
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at the URL shown above"
echo ""
echo "📋 Next steps:"
echo "1. Set environment variables in Vercel dashboard"
echo "2. Test your application"
echo "3. Set up external services if using full version" 