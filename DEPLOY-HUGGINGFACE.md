# Deploy TaskPilot Backend to Hugging Face Spaces

## Quick Setup Guide

---

## Step 1: Create a Hugging Face Space

1. **Go to**: https://huggingface.co/spaces

2. **Click**: "Create new Space"

3. **Configure**:
   - **Owner**: Your username (e.g., `Ambreeen17`)
   - **Space name**: `taskpilot-backend`
   - **License**: MIT
   - **SDK**: **Docker** (important!)
   - **Hardware**: **CPU basic** (free) or **CPU upgrade** ($5/month for better performance)
   - **Public**: Yes (or No if you want it private)

4. **Click**: "Create Space"

---

## Step 2: Prepare Backend for Hugging Face

Create these files in your `backend` folder:

### 1. Create `backend/Dockerfile` for Hugging Face:

```dockerfile
# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Hugging Face uses 7860)
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### 2. Update `backend/requirements.txt`:

Ensure it includes all necessary dependencies:
```
fastapi
uvicorn[standard]
sqlmodel
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
python-multipart
anthropic
python-dateutil
pytz
```

### 3. Create `backend/.dockerignore`:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.env
.venv
venv/
ENV/
tests/
.pytest_cache
.coverage
htmlcov/
```

---

## Step 3: Set Up Database on Neon (PostgreSQL)

1. **Go to**: https://neon.tech

2. **Sign up** (free tier available)

3. **Create a project**:
   - Name: `taskpilot`
   - Region: choose closest to you

4. **Get your connection string**:
   - Dashboard → Your Project → Connection Details
   - Copy the **Connection string** (format: `postgresql://...`)

5. **Save it** - you'll need it for environment variables

---

## Step 4: Push Backend to Hugging Face

### Option A: Via Git (Recommended)

1. **Open terminal** in your project folder

2. **Clone your Hugging Face Space**:
```bash
git clone https://huggingface.co/spaces/Ambreeen17/taskpilot-backend
cd taskpilot-backend
```

3. **Copy backend files**:
```bash
# Copy everything from your local backend folder to the cloned space
cp -r ../../../backend/* .
```

4. **Commit and push**:
```bash
git add .
git commit -m "Initial deployment of TaskPilot backend"
git push
```

5. **Hugging Face will automatically build and deploy**

### Option B: Via Web Interface

1. Go to your Space: https://huggingface.co/spaces/Ambreeen17/taskpilot-backend

2. Click **"Files"** → **"Add file"** → **"Upload files"**

3. Upload these files/folders from your `backend` folder:
   - `src/`
   - `requirements.txt`
   - `Dockerfile`
   - `migrations/`

4. For each file, click "Commit changes to main"

---

## Step 5: Configure Environment Variables

1. **Go to**: Your Hugging Face Space → Settings

2. **Click**: "Repository secrets"

3. **Add secrets**:

| Secret Key | Value |
|------------|-------|
| `DATABASE_URL` | Your Neon PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `AI_FEATURES_ENABLED` | `true` |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` |
| `ANTHROPIC_MAX_TOKENS` | `1024` |

4. **Click** "Add" for each secret

---

## Step 6: Run Database Migrations

1. **Go to**: Your Space → "Logs"

2. **Wait** for the build to complete (~5 minutes)

3. **Once running**, you'll see:
```
Application startup complete.
Uvicorn running on http://0.0.0.0:7860
```

4. **Go to**: https://huggingface.co/spaces/Ambreeen17/taskpilot-backend/tree/main

5. **Click**: "Settings" → "Runtime"

6. **Type** in the console:
```bash
python -c "from src.database import engine; from sqlmodel import SQLModel; from src.models import User, Task; SQLModel.metadata.create_all(engine)"
```

Or visit your Space URL + `/docs` to see API documentation:
```
https://ambreeen17-taskpilot-backend.hf.space/docs
```

---

## Step 7: Update Frontend for Hugging Face Backend

Edit `frontend/next.config.ts`:

```typescript
const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://ambreeen17-taskpilot-backend.hf.space/:path*",
      },
    ];
  },
};

export default nextConfig;
```

Or update `frontend/src/lib/config.ts`:

```typescript
export const API_URL = "https://ambreeen17-taskpilot-backend.hf.space";
```

---

## Your URLs

### Backend
- **Hugging Face Space**: https://huggingface.co/spaces/Ambreeen17/taskpilot-backend
- **API Endpoint**: https://ambreeen17-taskpilot-backend.hf.space
- **API Docs**: https://ambreeen17-taskpilot-backend.hf.space/docs
- **Health Check**: https://ambreeen17-taskpilot-backend.hf.space/ai/health

### Frontend
- **Vercel**: Your Vercel URL (after deployment)

---

## Verification Checklist

- [ ] Hugging Face Space is created
- [ ] Backend files are uploaded
- [ ] Space builds successfully
- [ ] Environment variables are set
- [ ] Database is created on Neon
- [ ] Migrations are run
- [ ] API is accessible at the Space URL
- [ ] `/docs` page shows API documentation
- [ ] Frontend can connect to backend
- [ ] Can create accounts and tasks

---

## Advantages of Hugging Face Spaces

✅ **Free hosting** for CPU basic tier
✅ **Fast builds** with Docker
✅ **Auto-deploys** on git push
✅ **Public API** endpoint
✅ **Built-in monitoring** and logs
✅ **Easy scaling** to better hardware
✅ **Community visibility** for your project

---

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Check the "Logs" tab for errors

### Database Connection Errors
- Verify DATABASE_URL is correct
- Check Neon database is active
- Ensure database migrations ran

### API Returns 404
- Wait for build to complete
- Check the "Runtime" tab for startup logs
- Verify port is set to 7860

### Slow Performance
- Upgrade to "CPU upgrade" tier ($5/month)
- Optimize database queries
- Consider caching frequent requests

---

## Next Steps

1. Deploy backend to Hugging Face
2. Deploy frontend to Vercel
3. Test the full application
4. Share your links! 🚀

---

**Your Backend URL**: `https://ambreeen17-taskpilot-backend.hf.space`
