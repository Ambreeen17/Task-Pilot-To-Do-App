# TaskPilot Deployment Guide

## Overview
This guide will help you deploy TaskPilot to production:
- **Frontend**: Vercel
- **Backend**: Render
- **Database**: Neon PostgreSQL (via Render)

---

## Step 1: Push to GitHub

### Option A: Using GitHub Desktop (Easiest)
1. Open GitHub Desktop
2. File → Add Local Repository → Select this folder
3. Publish repository → Choose `Ambreeen17/Task-Pilot-To-Do-App`
4. Click "Publish"

### Option B: Using Command Line
1. Open Git Bash or PowerShell in this folder
2. Run:
```bash
git push -u origin master
```
3. When prompted for username: `Ambreeen17`
4. When prompted for password: Use your **GitHub Personal Access Token** (not your password)

### Create Personal Access Token (if needed):
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Generate and copy the token
5. Use this token instead of your password when pushing

---

## Step 2: Deploy Backend to Render

1. Go to: https://dashboard.render.com

2. Click **"New +"** → **"Web Service"**

3. Connect GitHub:
   - Click "Connect GitHub"
   - Authorize Render
   - Select `Task-Pilot-To-Do-App`
   - Click "Connect"

4. Configure Backend:
   - **Name**: `taskpilot-backend`
   - **Environment**: `Python 3`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

5. Environment Variables (click "Advanced" → "Add Environment Variable"):
   ```
   DATABASE_URL=your_neon_database_url
   ANTHROPIC_API_KEY=your_anthropic_api_key
   AI_FEATURES_ENABLED=true
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
   ANTHROPIC_MAX_TOKENS=1024
   ```

6. Database:
   - Click "New +" → "PostgreSQL"
   - Name: `taskpilot-db`
   - Database: `taskpilot`
   - User: `taskpilot_user`
   - Region: closest to you
   - Copy the **Internal Database URL** (format: `postgresql://...`)
   - Use this as `DATABASE_URL` in backend environment variables

7. Click **"Deploy"**

8. Run Migrations:
   - Go to your deployed service → "Events"
   - Click "Shell" button
   - Run: `python -c "from src.database import engine; from sqlmodel import SQLModel; from src.models import User, Task; SQLModel.metadata.create_all(engine)"`

**Save your Backend URL**: `https://taskpilot-backend.onrender.com`

---

## Step 3: Deploy Frontend to Vercel

1. Go to: https://vercel.com/ambreen-rais-projects

2. Click **"Add New..."** → **"Project"**

3. Import Git Repository:
   - Select `Ambreeen17/Task-Pilot-To-Do-App`
   - Click "Import"

4. Configure Project:
   - **Name**: `taskpilot-frontend`
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

5. Environment Variables:
   - Click "Environment Variables"
   - Add: `NEXT_PUBLIC_API_URL` = `https://taskpilot-backend.onrender.com`

6. Click **"Deploy"**

7. Wait for deployment (~2-3 minutes)

**Your Live App URL**: `https://taskpilot-frontend.vercel.app`

---

## Step 4: Update Frontend API URL

After deploying backend, you need to update the frontend's API configuration:

### Option A: Update in Vercel Dashboard
1. Go to your Vercel project → Settings → Environment Variables
2. Find `NEXT_PUBLIC_API_URL`
3. Update it to your Render backend URL
4. Redeploy

### Option B: Update Code Locally & Push
Edit `frontend/src/lib/config.ts`:
```typescript
export const API_URL = "https://taskpilot-backend.onrender.com";
```
Then commit and push:
```bash
git add frontend/src/lib/config.ts
git commit -m "chore: update API URL for production"
git push
```

---

## Verification Checklist

- [ ] GitHub repo updated: https://github.com/Ambreeen17/Task-Pilot-To-Do-App
- [ ] Backend deployed on Render: Check https://taskpilot-backend.onrender.com/docs
- [ ] Frontend deployed on Vercel: Check your Vercel URL
- [ ] Can access the app
- [ ] Can sign up/login
- [ ] Can create tasks manually
- [ ] AI chatbot works
- [ ] Can create tasks via chatbot
- [ ] Tasks appear in task list

---

## Important URLs to Save

- **GitHub Repository**: https://github.com/Ambreeen17/Task-Pilot-To-Do-App
- **Vercel Dashboard**: https://vercel.com/ambreen-rais-projects
- **Render Dashboard**: https://dashboard.render.com
- **Backend URL** (after deployment): `https://taskpilot-backend.onrender.com`
- **Frontend URL** (after deployment): Your Vercel URL

---

## Troubleshooting

### Backend Issues
- Check logs in Render Dashboard
- Ensure DATABASE_URL is correct
- Ensure ANTHROPIC_API_KEY is set

### Frontend Issues
- Check Vercel deployment logs
- Ensure NEXT_PUBLIC_API_URL points to your backend
- Check browser console for errors

### GitHub Push Issues
- Use Personal Access Token instead of password
- Ensure you have access to the repository
- Check: https://github.com/settings/tokens

---

## Next Steps

After successful deployment:

1. **Share your app links:**
   - Frontend URL (Vercel)
   - Backend API docs (Render)

2. **Monitor usage:**
   - Vercel Analytics
   - Render Metrics
   - Database usage

3. **Set up custom domain** (optional):
   - In Vercel: Settings → Domains
   - In Render: Settings → Custom Domains

---

## Support

If you encounter issues:
1. Check Render logs for backend errors
2. Check Vercel logs for frontend errors
3. Verify environment variables
4. Ensure database migrations ran successfully

Good luck! 🚀
