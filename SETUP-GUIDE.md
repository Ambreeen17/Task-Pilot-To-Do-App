# 🚀 Quick Setup Guide - Create Your Own Repos

## Step 1: Create GitHub Repository (2 minutes)

1. **Open**: https://github.com/new

2. **Fill in**:
   - Repository name: `TaskPilot` (or any name you like)
   - Description: `AI-powered task management app`
   - **Public**: ✅ (check the box)
   - **IMPORTANT**: Do NOT initialize with README, .gitignore, or license

3. **Click**: "Create repository"

4. **Copy your repository URL** (will be like: `https://github.com/YOUR_USERNAME/TaskPilot`)

---

## Step 2: Push to Your GitHub Repository (1 minute)

After creating the repository, open PowerShell and run:

```powershell
cd "C:\Users\User\Desktop\Task-Pilot-To-Do-App-005-adaptive-intelligence"

# Replace YOUR_USERNAME with your actual GitHub username
git remote set-url origin https://github.com/YOUR_USERNAME/TaskPilot.git

# Push (will prompt for credentials)
git push origin master
```

---

## Step 3: Create Hugging Face Space (2 minutes)

1. **Open**: https://huggingface.co/spaces

2. **Click**: "Create new Space"

3. **Fill in**:
   - Owner: Your username (will be selected by default)
   - Space name: `taskpilot-backend`
   - License: `MIT`
   - SDK: `Docker`
   - Hardware: `CPU basic` (free)
   - Public: ✅

4. **Click**: "Create Space"

5. **Copy your space URL** (will be like: `https://huggingface.co/spaces/YOUR_USERNAME/taskpilot-backend`)

---

## Step 4: Push Backend to Hugging Face (2 minutes)

After creating the space, open PowerShell and run:

```powershell
cd "C:\Users\User\Desktop\Task-Pilot-To-Do-App-005-adaptive-intelligence\hf-deploy\bk"

# Replace YOUR_USERNAME with your Hugging Face username
git remote set-url origin https://huggingface.co/spaces/YOUR_USERNAME/taskpilot-backend

# Push (will prompt for credentials)
git push origin main
```

---

## Step 5: Configure Environment Variables (3 minutes)

### On Hugging Face:
1. Go to your Space → Settings
2. Click "New secret"
3. Add these secrets:

```
DATABASE_URL = get_from_neon (see step 6)
ANTHROPIC_API_KEY = your_anthropic_key
AI_FEATURES_ENABLED = true
ANTHROPIC_MODEL = claude-3-5-sonnet-20241022
ANTHROPIC_MAX_TOKENS = 1024
```

### On Neon (Database):
1. Go to: https://neon.tech
2. Sign up (free)
3. Click "Create a project"
4. Name: `taskpilot`
5. Click "Create Project"
6. Copy the **Connection string**
7. Add it as `DATABASE_URL` in Hugging Face (above)

---

## Step 6: Deploy Frontend to Vercel (2 minutes)

1. Go to: https://vercel.com/ambreen-rais-projects
2. Click "Add New..." → "Project"
3. Import your GitHub repository (from Step 2)
4. Configure:
   - Root Directory: `frontend`
   - Framework: Next.js
   - Build Command: `npm run build`
5. Environment Variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://YOUR_USERNAME-taskpilot-backend.hf.space`
6. Click "Deploy"

---

## ✅ Your URLs After Deployment

- **GitHub**: https://github.com/YOUR_USERNAME/TaskPilot
- **Hugging Face**: https://huggingface.co/spaces/YOUR_USERNAME/taskpilot-backend
- **Backend API**: https://YOUR_USERNAME-taskpilot-backend.hf.space
- **Frontend App**: Your Vercel URL (shown after deployment)

---

## 🎯 Total Time: ~12 minutes

1. Create GitHub repo: 2 min
2. Push to GitHub: 1 min
3. Create HF Space: 2 min
4. Push to HF: 2 min
5. Configure env vars: 3 min
6. Deploy frontend: 2 min

---

**Ready? Start with Step 1!** 🚀

---

## Need Help?

If you get stuck at any step, tell me:
1. Which step you're on
2. What error message you see
3. What you're trying to do

I'll help you fix it! 💪
