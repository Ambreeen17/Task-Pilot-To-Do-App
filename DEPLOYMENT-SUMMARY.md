# TaskPilot - Complete Deployment Guide

## 🚀 Deployment Architecture

```
┌─────────────────┐
│   Vercel        │  ← Frontend (Next.js)
│   Frontend      │     https://taskpilot.vercel.app
└────────┬────────┘
         │
         │ API Calls
         ▼
┌─────────────────┐
│  Hugging Face   │  ← Backend (FastAPI)
│   Spaces        │     https://taskpilot-backend.hf.space
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Neon        │  ← Database (PostgreSQL)
│   PostgreSQL    │     Cloud-hosted
└─────────────────┘
```

---

## 📋 Quick Deployment Steps

### Step 1: Push Code to GitHub (5 min)

Open PowerShell in this folder and run:
```bash
git push -u origin master
```

**Authentication**:
- Username: `Ambreeen17`
- Password: Your GitHub Personal Access Token

**Get token**: https://github.com/settings/tokens/new?scopes=repo

---

### Step 2: Deploy Backend to Hugging Face (10 min)

#### A. Create Space
1. Go to: https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure:
   - Name: `taskpilot-backend`
   - SDK: **Docker**
   - Hardware: **CPU basic** (free)
   - Make Public

#### B. Upload Backend Files
Clone your Space and copy backend files:
```bash
git clone https://huggingface.co/spaces/Ambreeen17/taskpilot-backend
cd taskpilot-backend
cp -r ../backend/* .
git add .
git commit -m "Deploy TaskPilot backend"
git push
```

Or upload via web interface at: https://huggingface.co/spaces/Ambreeen17/taskpilot-backend/tree/main

**Files to upload**:
- `src/` folder
- `requirements.txt`
- `Dockerfile.huggingface` (rename to `Dockerfile`)
- `migrations/`

#### C. Set Environment Variables
Go to: Settings → Repository secrets

Add these secrets:
```
DATABASE_URL = your_neon_postgres_url
ANTHROPIC_API_KEY = your_anthropic_key
AI_FEATURES_ENABLED = true
ANTHROPIC_MODEL = claude-3-5-sonnet-20241022
ANTHROPIC_MAX_TOKENS = 1024
```

#### D. Create Database
1. Go to: https://neon.tech
2. Sign up (free)
3. Create project: `taskpilot`
4. Copy connection string
5. Add as `DATABASE_URL` secret

#### E. Run Migrations
Once Space is running, go to Runtime → Console and run:
```bash
python -c "from src.database import engine; from sqlmodel import SQLModel; from src.models import User, Task; SQLModel.metadata.create_all(engine)"
```

#### F. Test Backend
Visit: https://ambreeen17-taskpilot-backend.hf.space/docs

**Save this URL**: `https://ambreeen17-taskpilot-backend.hf.space`

---

### Step 3: Deploy Frontend to Vercel (5 min)

1. Go to: https://vercel.com/ambreen-rais-projects
2. Click "Add New..." → "Project"
3. Import GitHub repo: `Task-Pilot-To-Do-App`
4. Configure:
   - Root Directory: `frontend`
   - Framework: Next.js
5. Environment Variables:
   - `NEXT_PUBLIC_API_URL` = `https://ambreeen17-taskpilot-backend.hf.space`
6. Click "Deploy"

**Your App URL**: `https://taskpilot-frontend.vercel.app`

---

## ✅ Verification

Test your deployed app:

1. **Frontend loads**: https://taskpilot-frontend.vercel.app
2. **Can sign up**: Create new account
3. **Can login**: Sign in with credentials
4. **Create task**: Manual task creation works
5. **AI Chatbot**: Chat interface loads
6. **Create via chat**: Type "Create task to test"
7. **Task appears**: Check task list

---

## 🔗 Important URLs

### GitHub
- **Repository**: https://github.com/Ambreeen17/Task-Pilot-To-Do-App
- **Issues**: https://github.com/Ambreeen17/Task-Pilot-To-Do-App/issues

### Backend (Hugging Face)
- **Space**: https://huggingface.co/spaces/Ambreeen17/taskpilot-backend
- **API**: https://ambreeen17-taskpilot-backend.hf.space
- **API Docs**: https://ambreeen17-taskpilot-backend.hf.space/docs
- **Health**: https://ambreeen17-taskpilot-backend.hf.space/ai/health

### Frontend (Vercel)
- **App**: https://taskpilot-frontend.vercel.app
- **Dashboard**: https://vercel.com/ambreen-rais-projects
- **Analytics**: https://vercel.com/ambreen-rais-projects/taskpilot-frontend/analytics

### Database (Neon)
- **Dashboard**: https://console.neon.tech
- **Connection**: Check your Neon console

---

## 🛠️ Troubleshooting

### Backend Issues

**Space not building**:
- Check "Logs" tab on Hugging Face
- Verify Dockerfile syntax
- Ensure all dependencies in requirements.txt

**Database connection failed**:
- Verify DATABASE_URL secret
- Check Neon database is active
- Test connection string format

**AI not working**:
- Verify ANTHROPIC_API_KEY secret
- Check AI_FEATURES_ENABLED = true
- Visit `/ai/health` endpoint

### Frontend Issues

**App not loading**:
- Check Vercel deployment logs
- Verify build succeeded
- Check browser console for errors

**Can't connect to backend**:
- Verify NEXT_PUBLIC_API_URL in Vercel
- Check backend is running on Hugging Face
- Test backend URL directly

**Tasks not saving**:
- Check backend logs
- Verify database connection
- Ensure migrations ran

---

## 📊 Monitoring

### Hugging Face (Backend)
- Space logs and metrics
- API request counts
- Error rates
- CPU/memory usage

### Vercel (Frontend)
- Page views
- Performance metrics
- Build logs
- Analytics

### Neon (Database)
- Query performance
- Storage usage
- Connection count
- Active queries

---

## 🎯 Next Steps

### Phase 1: Basic Deployment
- [x] Code committed locally
- [ ] Pushed to GitHub
- [ ] Backend on Hugging Face
- [ ] Frontend on Vercel
- [ ] Database on Neon

### Phase 2: Testing
- [ ] Test all features
- [ ] Verify AI chatbot
- [ ] Check task creation
- [ ] Test authentication

### Phase 3: Customization (Optional)
- [ ] Add custom domain
- [ ] Set up analytics
- [ ] Configure monitoring
- [ ] Add error tracking (Sentry)

### Phase 4: Enhancement (Future)
- [ ] Add more AI features
- [ ] Improve UI/UX
- [ ] Add mobile app
- [ ] Implement reminders

---

## 💰 Cost Estimate

### Free Tier Usage
- **Hugging Face**: $0/month (CPU basic)
- **Vercel**: $0/month (hobby plan)
- **Neon**: $0/month (free tier 0.5GB)

### Paid Upgrades (if needed)
- **Hugging Face CPU upgrade**: $5/month
- **Vercel Pro**: $20/month
- **Neon Paid**: Starts at $19/month

**Total free tier**: $0/month ✅

---

## 📞 Support

If you need help:
1. Check this guide's troubleshooting section
2. Review Hugging Face Space logs
3. Check Vercel deployment logs
4. Verify all environment variables
5. Test endpoints individually

---

## 🎉 Success!

Once deployed, you'll have:
- **Full-stack AI task manager**
- **Working chatbot interface**
- **Bilingual support (English/Urdu)**
- **Cloud-hosted and scalable**
- **100% free hosting**

**Share your app**: https://taskpilot-frontend.vercel.app

---

**Made with ❤️ by Ambreen**
