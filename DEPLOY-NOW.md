# Deploy TaskPilot - Quick Start

## 🚀 Deploy in 3 Steps

### Step 1: Push to GitHub (2 min)

Run this in PowerShell from your project folder:

```powershell
cd "C:\Users\User\Desktop\Task-Pilot-To-Do-App-005-adaptive-intelligence"
git push -u origin master
```

**If asked for credentials:**
- Username: `Ambreeen17`
- Password: Your GitHub Personal Access Token

**Get token**: https://github.com/settings/tokens/new?scopes=repo

---

### Step 2: Push Backend to Hugging Face (3 min)

**Option A: Use the script** (Double-click)
- Open folder in File Explorer
- Double-click: `push-to-huggingface.bat`

**Option B: Manual push**
1. Get your Hugging Face token: https://huggingface.co/settings/tokens
2. Create a token with "Write" permissions
3. Run in PowerShell:
```powershell
cd "C:\Users\User\Desktop\Task-Pilot-To-Do-App-005-adaptive-intelligence\hf-deploy\bk"
git push https://ambreenaz:YOUR_TOKEN@huggingface.co/spaces/ambreenaz/bk main
```

**Replace `YOUR_TOKEN` with your actual Hugging Face token**

---

### Step 3: Configure & Deploy (5 min)

#### A. Set Environment Variables on Hugging Face

Go to: https://huggingface.co/spaces/ambreenaz/bk/settings

Click "New secret" and add these:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | See step B below |
| `ANTHROPIC_API_KEY` | Your Anthropic key |
| `AI_FEATURES_ENABLED` | `true` |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` |
| `ANTHROPIC_MAX_TOKENS` | `1024` |

#### B. Create Database

1. Go to: https://neon.tech
2. Sign up (free)
3. Click "Create a project"
4. Name: `taskpilot`
5. Click "Create Project"
6. Copy the **Connection string** (looks like: `postgresql://...`)
7. Paste it as `DATABASE_URL` in Hugging Face settings (step A)

#### C. Wait for Build

1. Go to: https://huggingface.co/spaces/ambreenaz/bk
2. Watch the "Logs" tab
3. Wait for: "Application startup complete" (~5-10 min)

#### D. Run Migrations

Once running, go to Settings → Runtime and run:
```python
python -c "from src.database import engine; from sqlmodel import SQLModel; from src.models import User, Task; SQLModel.metadata.create_all(engine)"
```

#### E. Test Backend

Visit: https://ambreenaz-bk.hf.space/docs

You should see the API documentation! ✅

---

### Step 4: Deploy Frontend to Vercel (2 min)

1. Go to: https://vercel.com/ambreen-rais-projects
2. Click "Add New..." → "Project"
3. Import: `Task-Pilot-To-Do-App`
4. Configure:
   - Root Directory: `frontend`
   - Framework: Next.js (auto-detected)
5. Environment Variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://ambreenaz-bk.hf.space`
6. Click "Deploy"

**Your app URL**: Will be shown after deployment (~2 min)

---

## ✅ Your Live URLs

### Backend
- **Space**: https://huggingface.co/spaces/ambreenaz/bk
- **API**: https://ambreenaz-bk.hf.space
- **Docs**: https://ambreenaz-bk.hf.space/docs

### Frontend
- **App**: Your Vercel URL (after deployment)

---

## 🧪 Test Your App

1. Open your Vercel URL
2. Click "Sign Up"
3. Create an account
4. Create a task
5. Try the AI chatbot
6. Create a task via chat: "Create task to test deployment"

---

## 📊 What You Get

✅ Full-stack AI task manager
✅ Working chatbot interface
✅ Bilingual support (English/Urdu)
✅ Cloud-hosted (100% free)
✅ Scalable architecture

---

## 🆘 Troubleshooting

**Git push fails:**
- Use Personal Access Token, not password
- Verify token has "repo" scope

**Hugging Face push fails:**
- Check token has "Write" permissions
- Verify username is correct: `ambreenaz`

**Build fails on HF:**
- Check "Logs" tab
- Verify all files were uploaded
- Ensure Dockerfile is present

**Can't connect to database:**
- Verify DATABASE_URL is correct
- Check Neon database is active
- Test connection string format

**Frontend can't reach backend:**
- Verify NEXT_PUBLIC_API_URL in Vercel
- Check backend is running
- Test backend URL directly

---

## 🎉 Success!

Once deployed, share your links:
- Frontend: (Your Vercel URL)
- Backend: https://ambreenaz-bk.hf.space

**Made with ❤️ by Ambreen**
