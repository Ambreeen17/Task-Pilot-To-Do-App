# 🚀 Deploy TaskPilot - Quick Instructions

## Your Code is Ready!

All code is committed and ready to deploy. Here's what you need to do:

---

## Step 1: Push Backend to Hugging Face (1 min)

**Option A: Use the script** (Recommended)
- Go to folder: `C:\Users\User\Desktop\Task-Pilot-To-Do-App-005-adaptive-intelligence\hf-deploy-new\bk`
- Right-click: `push-to-hf.ps1`
- Select: "Run with PowerShell"

**Option B: Manual push in PowerShell**
```powershell
cd "C:\Users\User\Desktop\Task-Pilot-To-Do-App-005-adaptive-intelligence\hf-deploy-new\bk"
huggingface-cli login
git push origin main
```

---

## Step 2: Set Environment Variables (2 min)

1. Go to: https://huggingface.co/spaces/ambreenaz/bk/settings
2. Click "New secret" for each:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Get from Neon (Step 3) |
| `ANTHROPIC_API_KEY` | Your Anthropic key |
| `AI_FEATURES_ENABLED` | `true` |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` |
| `ANTHROPIC_MAX_TOKENS` | `1024` |

---

## Step 3: Create Database (2 min)

1. Go to: https://neon.tech
2. Sign up (free)
3. Click: "Create a project"
4. Name: `taskpilot`
5. Click: "Create Project"
6. Copy the **Connection string** (looks like: `postgresql://...`)
7. Go back to Step 2 and add it as `DATABASE_URL`

---

## Step 4: Wait for Build (5-10 min)

1. Go to: https://huggingface.co/spaces/ambreenaz/bk
2. Watch the "Logs" tab
3. Wait for: "Application startup complete"

---

## Step 5: Run Migrations (1 min)

Once the Space is running:

1. Go to: Settings → Runtime
2. In the terminal, run:
```python
python -c "from src.database import engine; from sqlmodel import SQLModel; from src.models import User, Task; SQLModel.metadata.create_all(engine)"
```

---

## Step 6: Test Backend (30 seconds)

Visit: https://ambreenaz-bk.hf.space/docs

You should see the API documentation! ✅

---

## Step 7: Deploy Frontend to Vercel (2 min)

1. Go to: https://vercel.com/ambreen-rais-projects
2. Click: "Add New..." → "Project"
3. Import GitHub repo: `Task-Pilot-To-Do-App` (or the one you created)
4. Configure:
   - Root Directory: `frontend`
   - Framework: Next.js
5. Environment Variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://ambreenaz-bk.hf.space`
6. Click: "Deploy"

---

## 🎉 Your Live App

After deployment:

- **Backend API**: https://ambreenaz-bk.hf.space
- **API Docs**: https://ambreenaz-bk.hf.space/docs
- **Frontend App**: Your Vercel URL

---

## Total Time: ~15 minutes

1. Push to HF: 1 min
2. Set env vars: 2 min
3. Create database: 2 min
4. Wait for build: 5-10 min
5. Run migrations: 1 min
6. Deploy frontend: 2 min
7. Testing: 2 min

---

## ✅ Checklist

- [ ] Run `push-to-hf.ps1` script
- [ ] Set environment variables on Hugging Face
- [ ] Create database on Neon
- [ ] Wait for Hugging Face build
- [ ] Run migrations
- [ ] Test backend API
- [ ] Deploy frontend to Vercel
- [ ] Test the full app

---

**Start with Step 1!** 🚀

Everything is prepared and ready. Just follow the steps above!
