# Quick Deployment Guide - 5 Minutes

## Backend Deployment on Render (2 minutes)

### Step 1: Access Render Dashboard
1. Open your browser and go to: **https://dashboard.render.com**
2. Sign in with your GitHub account (or create a free account)

### Step 2: Deploy via Blueprint (One-Click)
1. Click the **"New +"** button (top right)
2. Select **"Blueprint"** from the dropdown menu
3. **Connect GitHub Repository**:
   - If not connected: Click "Connect GitHub" and authorize Render
   - Select your repository: **`Ambreeen17/TO-DO-APP-PHASE1`**
   - Branch: **`phase-2`**
4. Click **"Apply"** button

### Step 3: Wait for Deployment (1-2 minutes)
Render will automatically:
- ✅ Create PostgreSQL database (`todo-db`)
- ✅ Deploy FastAPI backend (`todo-backend`)
- ✅ Generate secure `JWT_SECRET`
- ✅ Connect database to backend
- ✅ Install dependencies and start server

You'll see two services being created:
- `todo-backend` (Web Service)
- `todo-db` (PostgreSQL)

### Step 4: Get Your Backend URL
Once deployment completes (green checkmark):
1. Click on **`todo-backend`** service
2. Copy the URL at the top (looks like: `https://todo-backend-xxxx.onrender.com`)
3. **Save this URL** - you'll need it for frontend configuration

### Step 5: Test Your Backend
Open your backend URL in a browser:
```
https://todo-backend-xxxx.onrender.com/docs
```
You should see the **Swagger UI** documentation page.

---

## Frontend Configuration on Vercel (2 minutes)

### Step 1: Access Vercel Dashboard
1. Go to: **https://vercel.com/ambreen-rais-projects/frontend**
2. Click on your **frontend** project

### Step 2: Add Backend URL Environment Variable
1. Go to **Settings** tab (top navigation)
2. Click **Environment Variables** (left sidebar)
3. Click **"Add New"** button
4. Fill in:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://todo-backend-xxxx.onrender.com
   ```
   (Replace `xxxx` with your actual Render backend URL)
5. Select environments: **Production**, **Preview**, **Development** (all three)
6. Click **"Save"**

### Step 3: Update CORS on Backend
1. Go back to **Render Dashboard**
2. Click on **`todo-backend`** service
3. Go to **Environment** tab (left sidebar)
4. Find **`CORS_ORIGINS`** variable
5. **Verify** it has your Vercel URL:
   ```
   https://frontend-ordvthoae-ambreen-rais-projects.vercel.app
   ```
   (If different, update it and service will auto-redeploy)

### Step 4: Redeploy Frontend
1. Go back to **Vercel Dashboard** → Your frontend project
2. Go to **Deployments** tab
3. Click **"..."** (three dots) on the latest deployment
4. Select **"Redeploy"**
5. Confirm the redeploy

---

## Verification (1 minute)

### Test the Complete Application

1. **Open Your Live App**:
   ```
   https://frontend-ordvthoae-ambreen-rais-projects.vercel.app
   ```

2. **Create Account**:
   - Click "Sign up"
   - Enter email and password (min 8 characters)
   - Click "Create Account"

3. **Login**:
   - Enter your credentials
   - Click "Sign In"

4. **Create a Task**:
   - Enter task title (e.g., "Test Task")
   - Add description (optional)
   - Select priority
   - Click "Create Task"

5. **Verify Task Appears**:
   - Task should appear in the list below
   - Try toggling completion status
   - Try deleting the task

### ✅ If all steps work, deployment is complete!

---

## Troubleshooting

### Issue: Backend deployment fails
**Solution**:
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Ensure Python version is compatible

### Issue: Frontend shows "Failed to connect"
**Solution**:
- Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Check backend URL is accessible (open in browser)
- Verify CORS_ORIGINS includes your Vercel URL

### Issue: CORS errors in browser console
**Solution**:
- Go to Render → `todo-backend` → Environment
- Update `CORS_ORIGINS` to include your Vercel URL
- Service will auto-redeploy

### Issue: Authentication not working
**Solution**:
- Clear browser cookies and localStorage
- Re-register with a new email
- Check backend logs in Render dashboard

---

## Important Notes

### Free Tier Limitations

**Render Free Tier**:
- Backend sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start)
- Database: 1GB storage, limited connection hours

**Vercel Free Tier**:
- Unlimited deployments
- 100GB bandwidth/month
- Automatic SSL certificates

### Cost: $0/month for both services

---

## Next Steps After Deployment

1. ✅ Test all features (create, read, update, delete tasks)
2. ✅ Test search and filter functionality
3. ✅ Share your live app URL with others
4. 📋 Optional: Set up custom domain
5. 📋 Optional: Add monitoring and alerts
6. 🚀 Move to Phase 3: AI-Powered Layer

---

## Quick Reference

### Your URLs
- **Frontend**: https://frontend-ordvthoae-ambreen-rais-projects.vercel.app
- **Backend**: https://todo-backend-xxxx.onrender.com (after deployment)
- **Backend API Docs**: https://todo-backend-xxxx.onrender.com/docs

### Dashboards
- **Render**: https://dashboard.render.com
- **Vercel**: https://vercel.com/ambreen-rais-projects

### Environment Variables
- **Backend** (Render):
  - `JWT_SECRET` - Auto-generated
  - `DATABASE_URL` - Auto-configured
  - `CORS_ORIGINS` - Your Vercel URL

- **Frontend** (Vercel):
  - `NEXT_PUBLIC_API_URL` - Your Render backend URL

---

## Support

- Full documentation: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- Backend logs: Render Dashboard → Service → Logs
- Frontend logs: Vercel Dashboard → Deployment → Build Logs
