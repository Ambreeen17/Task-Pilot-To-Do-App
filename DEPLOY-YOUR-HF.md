# Deploy TaskPilot Backend to YOUR Hugging Face Space

## Your Hugging Face Space
**URL**: https://huggingface.co/spaces/ambreenaz/bk

---

## Quick Deployment (5-10 minutes)

### Step 1: Prepare Files

1. **Copy Dockerfile**:
   - From: `backend/Dockerfile.huggingface`
   - To: `backend/Dockerfile`
   - (Rename it to just `Dockerfile`)

2. **Prepare backend folder contents**:
   - `src/` folder (all Python code)
   - `requirements.txt`
   - `Dockerfile` (the one you renamed)
   - `migrations/` folder

### Step 2: Push to Your Hugging Face Space

#### Option A: Via Git (Recommended)

1. **Open terminal** in your project folder

2. **Clone your Space**:
```bash
git clone https://huggingface.co/spaces/ambreenaz/bk
cd bk
```

3. **Copy backend files**:
```bash
# From your project root
cp -r backend/* .
cp backend/Dockerfile.huggingface Dockerfile
```

4. **Commit and push**:
```bash
git add .
git commit -m "Deploy TaskPilot backend"
git push
```

5. **Hugging Face will automatically build** 🎉

#### Option B: Via Web Interface

1. **Go to**: https://huggingface.co/spaces/ambreenaz/bk/tree/main

2. **Click**: "Add file" → "Upload files"

3. **Upload these folders/files**:
   - Upload entire `src/` folder
   - Upload `requirements.txt`
   - Upload `Dockerfile.huggingface` as `Dockerfile`
   - Upload `migrations/` folder

4. **Click** "Commit changes to main" for each upload

---

## Step 3: Set Environment Variables

1. **Go to**: https://huggingface.co/spaces/ambreenaz/bk/settings

2. **Scroll to**: "Repository secrets"

3. **Click**: "New secret"

4. **Add these secrets** one by one:

| Secret Key | Value | How to get |
|------------|-------|------------|
| `DATABASE_URL` | Your Neon connection string | See Step 4 |
| `ANTHROPIC_API_KEY` | Your Anthropic key | https://console.anthropic.com |
| `AI_FEATURES_ENABLED` | `true` | Type: true |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` | Type: claude-3-5-sonnet-20241022 |
| `ANTHROPIC_MAX_TOKENS` | `1024` | Type: 1024 |

5. **Click** "Add" for each secret

---

## Step 4: Set Up Database (Neon)

1. **Go to**: https://neon.tech

2. **Sign up/Login** (free tier available)

3. **Click**: "Create a project"

4. **Configure**:
   - Name: `taskpilot`
   - Region: AWS us-east-1 (or closest to you)
   - Click "Create Project"

5. **Get connection string**:
   - Dashboard → Your project
   - Click "Connection Details"
   - Copy the **Connection string** (looks like: `postgresql://...`)

6. **Add it** as `DATABASE_URL` secret in Hugging Face (Step 3)

---

## Step 5: Run Database Migrations

1. **Wait for build** (~5-10 minutes)
   - Go to: https://huggingface.co/spaces/ambreenaz/bk
   - Watch the "Logs" tab
   - Wait for: "Application startup complete"

2. **Once running**, go to Settings → Runtime

3. **In the terminal**, run:
```bash
python -c "from src.database import engine; from sqlmodel import SQLModel; from src.models import User, Task; SQLModel.metadata.create_all(engine)"
```

4. **You should see**: No errors = success! ✅

---

## Step 6: Test Your Backend

1. **API Documentation**: https://ambreenaz-bk.hf.space/docs

2. **Health Check**: https://ambreenaz-bk.hf.space/ai/health

3. **Test endpoint**: https://ambreenaz-bk.hf.space/ai/health
   Should return:
   ```json
   {
     "status": "ok",
     "api_key_configured": true,
     "features_enabled": true
   }
   ```

**Save this URL**: `https://ambreenaz-bk.hf.space`

---

## Step 7: Deploy Frontend to Vercel

1. **Go to**: https://vercel.com/ambreen-rais-projects

2. **Click**: "Add New..." → "Project"

3. **Import**: GitHub repo `Task-Pilot-To-Do-App`

4. **Configure**:
   - Root Directory: `frontend`
   - Framework Preset: Next.js
   - Everything else: Auto-detected

5. **Environment Variables**:
   - Click "Environment Variables"
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://ambreenaz-bk.hf.space`

6. **Click**: "Deploy"

7. **Your frontend URL**: Will be like `https://taskpilot-xxxx.vercel.app`

---

## Your URLs

### Backend
- **Space**: https://huggingface.co/spaces/ambreenaz/bk
- **API**: https://ambreenaz-bk.hf.space
- **API Docs**: https://ambreenaz-bk.hf.space/docs
- **Health**: https://ambreenaz-bk.hf.space/ai/health

### Frontend
- **App**: Your Vercel URL (after deployment)
- **Dashboard**: https://vercel.com/ambreen-rais-projects

---

## Testing Checklist

- [ ] Backend builds successfully on Hugging Face
- [ ] Database environment variable is set
- [ ] Anthropic API key is set
- [ ] Migrations ran successfully
- [ ] `/docs` page loads
- [ ] `/ai/health` returns "ok"
- [ ] Frontend deploys to Vercel
- [ ] Can access the app
- [ ] Can sign up
- [ ] Can create tasks
- [ ] AI chatbot works

---

## Troubleshooting

### Build fails
- Check "Logs" tab on Hugging Face
- Verify Dockerfile is in place
- Ensure requirements.txt has all dependencies

### "Module not found" errors
- Make sure `src/` folder was uploaded
- Check all subfolders are included
- Verify structure: `src/main.py`, `src/models/`, etc.

### Database errors
- Verify DATABASE_URL secret
- Check Neon database is active
- Test connection string format

### API returns errors
- Check all secrets are set
- Verify ANTHROPIC_API_KEY is valid
- Ensure AI_FEATURES_ENABLED = "true"

### Frontend can't connect
- Verify NEXT_PUBLIC_API_URL in Vercel
- Check backend is running
- Test backend URL directly in browser

---

## Support Links

- **Your Space**: https://huggingface.co/spaces/ambreenaz/bk
- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **Neon Docs**: https://neon.tech/docs
- **Vercel Docs**: https://vercel.com/docs

---

## Quick Reference

### Git Commands for Hugging Face
```bash
# Clone your space
git clone https://huggingface.co/spaces/ambreenaz/bk
cd bk

# Make changes
cp -r ../backend/* .

# Commit and push
git add .
git commit -m "Update backend"
git push
```

### Update Existing Deployment
```bash
cd bk
git pull
# Make changes
git add .
git commit -m "Update"
git push
```

---

**You're all set!** 🚀

Backend: https://ambreenaz-bk.hf.space
Frontend: (After Vercel deployment)
