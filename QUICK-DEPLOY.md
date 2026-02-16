# Quick Deployment Checklist

## ✅ Pre-Deployment

1. **All code is committed locally** ✓
2. **Git repository is initialized** ✓
3. **Ready to push to GitHub** ⏳

---

## 📋 Step-by-Step

### 1️⃣ PUSH TO GITHUB (5 minutes)

**Open PowerShell or Git Bash in this folder and run:**

```bash
git push -u origin master
```

**If it asks for credentials:**
- Username: `Ambreeen17`
- Password: Your GitHub Personal Access Token

**Don't have a token?** Create one here:
https://github.com/settings/tokens/new?scopes=repo

---

### 2️⃣ DEPLOY BACKEND TO RENDER (10 minutes)

1. **Go to**: https://dashboard.render.com
2. **Click**: "New +" → "Web Service"
3. **Connect**: Your GitHub repo `Task-Pilot-To-Do-App`
4. **Settings**:
   - Name: `taskpilot-backend`
   - Environment: `Python 3`
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

5. **Environment Variables** (click "Advanced" → "Add"):
   ```
   DATABASE_URL=get_from_render_postgres
   ANTHROPIC_API_KEY=your_key_here
   AI_FEATURES_ENABLED=true
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
   ANTHROPIC_MAX_TOKENS=1024
   ```

6. **Create Database**:
   - "New +" → "PostgreSQL"
   - Name: `taskpilot-db`
   - Copy the **Internal Database URL**
   - Add it as `DATABASE_URL` in backend environment variables

7. **Click**: "Deploy"

8. **Run Migrations** (after deploy):
   - Go to service → "Events" → "Shell"
   - Run: `python -c "from src.database import engine; from sqlmodel import SQLModel; from src.models import User, Task; SQLModel.metadata.create_all(engine)"`

**Save this URL**: `https://taskpilot-backend.onrender.com`

---

### 3️⃣ DEPLOY FRONTEND TO VERCEL (5 minutes)

1. **Go to**: https://vercel.com/ambreen-rais-projects
2. **Click**: "Add New..." → "Project"
3. **Import**: `Ambreeen17/Task-Pilot-To-Do-App`
4. **Configure**:
   - Root Directory: `frontend`
   - Framework: Next.js
   - Build & Install: Auto-detected
5. **Environment Variable**:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://taskpilot-backend.onrender.com`
6. **Click**: "Deploy"

**Your app URL**: `https://taskpilot-frontend.vercel.app`

---

## 🎯 Post-Deployment

1. **Test the app** at your Vercel URL
2. **Sign up** for a new account
3. **Create a task**
4. **Try the AI chatbot**
5. **Share your links!**

---

## 🔗 Important Links

- **GitHub**: https://github.com/Ambreeen17/Task-Pilot-To-Do-App
- **Vercel**: https://vercel.com/ambreen-rais-projects
- **Render**: https://dashboard.render.com

---

## 💡 Tips

- Keep your Anthropic API key secret
- Use Render's free tier for backend
- Use Vercel's free tier for frontend
- Monitor usage in both dashboards

---

## 🆘 Need Help?

- Check Render logs for backend errors
- Check Vercel logs for frontend errors
- Verify environment variables are set
- Ensure database migrations ran

---

**Ready to deploy? Start with Step 1!** 🚀
