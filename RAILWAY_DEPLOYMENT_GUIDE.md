# 🚀 Unitasa Railway Deployment Guide

## Complete deployment setup for Railway.app

---

## 📋 **Pre-Deployment Checklist**

### ✅ **Files Created:**
- `railway.json` - Railway configuration
- `nixpacks.toml` - Build configuration  
- `requirements.txt` - Python dependencies
- `app/main.py` - FastAPI application entry point
- `app/core/database.py` - Database configuration
- `app/core/config.py` - Environment settings
- `Procfile` - Process configuration
- `.env.railway` - Environment variables template
- `deploy.sh` - Deployment preparation script

---

## 🚀 **Railway Deployment Steps**

### **Step 1: Prepare Repository**
```bash
# Ensure all files are committed
git add .
git commit -m "Prepare Unitasa for Railway deployment"
git push origin main
```

### **Step 2: Create Railway Project**
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your Unitasa repository

### **Step 3: Add PostgreSQL Database**
1. In your Railway project dashboard
2. Click "New Service"
3. Select "Database" → "PostgreSQL"
4. Railway will automatically provide `DATABASE_URL`

### **Step 4: Configure Environment Variables**
Copy variables from `.env.railway` to Railway:

**Required Variables:**
```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-change-this
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
OPENAI_API_KEY=sk-your-openai-key
SENDGRID_API_KEY=SG.your-sendgrid-key
FROM_EMAIL=hello@unitasa.in
```

**Optional Variables:**
```env
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
SENTRY_DSN=your-sentry-dsn
ALLOWED_ORIGINS=https://unitasa.in,https://www.unitasa.in
```

### **Step 5: Deploy**
1. Railway will automatically deploy after configuration
2. Monitor deployment logs in Railway dashboard
3. Your app will be available at: `https://your-app.railway.app`

---

## 🔧 **Configuration Details**

### **Railway.json Configuration**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### **Nixpacks Build Process**
1. **Setup**: Install Node.js 18, Python 3.11, PostgreSQL
2. **Install**: Install npm and pip dependencies
3. **Build**: Build React frontend
4. **Start**: Run FastAPI server with uvicorn

### **Application Architecture**
```
Railway App
├── FastAPI Backend (Python)
├── React Frontend (Built & Served)
├── PostgreSQL Database
└── Static File Serving
```

---

## 🌐 **Domain Configuration**

### **Custom Domain Setup**
1. In Railway project settings
2. Go to "Domains" tab
3. Add custom domain: `unitasa.in`
4. Configure DNS records:
   ```
   Type: CNAME
   Name: @
   Value: your-app.railway.app
   ```

### **SSL Certificate**
- Railway automatically provides SSL certificates
- HTTPS will be enabled automatically

---

## 📊 **Monitoring & Logging**

### **Railway Dashboard**
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and status

### **Health Check Endpoint**
```
GET /health
Response: {"status": "healthy", "service": "unitasa-api"}
```

### **Application Endpoints**
- **Frontend**: `https://your-app.railway.app/`
- **API**: `https://your-app.railway.app/api/v1/`
- **Health**: `https://your-app.railway.app/health`

---

## 🔒 **Security Configuration**

### **Environment Variables**
- All sensitive data stored as Railway environment variables
- No secrets in code repository
- Automatic SSL/TLS encryption

### **CORS Configuration**
```python
allow_origins=["https://unitasa.in", "https://www.unitasa.in"]
```

### **Security Headers**
- Implemented via SecurityMiddleware
- HTTPS enforcement
- Content Security Policy

---

## 💰 **Railway Pricing**

### **Starter Plan (Free)**
- $5 credit per month
- Perfect for development and testing
- Automatic sleep after inactivity

### **Pro Plan ($20/month)**
- Unlimited usage
- No sleep
- Priority support
- Custom domains

---

## 🚨 **Troubleshooting**

### **Common Issues**

**Build Failures:**
```bash
# Check build logs in Railway dashboard
# Verify all dependencies in requirements.txt
# Ensure frontend builds successfully
```

**Database Connection:**
```bash
# Verify PostgreSQL service is running
# Check DATABASE_URL environment variable
# Ensure async database configuration
```

**Static Files Not Loading:**
```bash
# Verify frontend/build directory exists
# Check static file mounting in main.py
# Ensure React build completed successfully
```

### **Debug Commands**
```bash
# Local testing
python -m uvicorn app.main:app --reload

# Check database connection
python -c "from app.core.database import engine; print('DB OK')"

# Verify environment
python -c "from app.core.config import settings; print(settings.environment)"
```

---

## 📈 **Performance Optimization**

### **Frontend Optimization**
- React build optimization enabled
- Gzip compression middleware
- Static file caching
- Service worker for PWA

### **Backend Optimization**
- Async database operations
- Connection pooling
- Response compression
- Health check endpoint

### **Database Optimization**
- Connection pooling (10 connections)
- Pool recycling (1 hour)
- Async operations
- Proper indexing

---

## 🔄 **CI/CD Pipeline**

### **Automatic Deployments**
1. Push to main branch
2. Railway detects changes
3. Automatic build and deploy
4. Zero-downtime deployment

### **Deployment Hooks**
```bash
# Pre-deployment
npm run build

# Post-deployment  
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

---

## ✅ **Deployment Verification**

### **Post-Deployment Checklist**
- [ ] Application loads at Railway URL
- [ ] Database connection working
- [ ] API endpoints responding
- [ ] Frontend assets loading
- [ ] Payment processing functional
- [ ] AI features operational
- [ ] Assessment flow working
- [ ] Co-creator program active

### **Testing Commands**
```bash
# Test API health
curl https://your-app.railway.app/health

# Test frontend
curl https://your-app.railway.app/

# Test API endpoint
curl https://your-app.railway.app/api/v1/landing/status
```

---

## 🎯 **Next Steps After Deployment**

1. **Configure Custom Domain**: Point unitasa.in to Railway
2. **Set up Monitoring**: Configure error tracking and analytics
3. **Enable Features**: Activate payment processing and AI features
4. **Launch Marketing**: Begin founder program promotion
5. **Monitor Performance**: Track metrics and optimize

---

**🎉 Your Unitasa platform is now ready for Railway deployment!**

The complete unified marketing intelligence platform with $497 founder program, AI capabilities, and interactive demos will be live and ready to onboard your first 25 co-creators.