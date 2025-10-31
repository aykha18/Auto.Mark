#!/bin/bash

# Unitasa Railway Deployment Script
echo "🚀 Preparing Unitasa for Railway deployment..."

# Build frontend
echo "📦 Building React frontend..."
cd frontend
npm ci
npm run build
cd ..

# Verify build
if [ ! -d "frontend/build" ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend build successful!"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Run tests (optional)
echo "🧪 Running tests..."
python -m pytest --tb=short

echo "✅ Deployment preparation complete!"
echo ""
echo "📋 Next steps for Railway deployment:"
echo "1. Push code to GitHub repository"
echo "2. Connect repository to Railway"
echo "3. Add PostgreSQL service to Railway project"
echo "4. Set environment variables from .env.railway"
echo "5. Deploy!"
echo ""
echo "🌐 Your Unitasa app will be available at: https://your-app.railway.app"