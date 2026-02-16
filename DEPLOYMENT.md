# Deployment Guide

This guide covers deploying the Evolution of Todo application to production.

## Backend Deployment (Render)

### Prerequisites
- GitHub account
- Render account (sign up at https://render.com)

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Push to GitHub** (Already done)
   ```bash
   git push origin phase-2
   ```

2. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Click "New +" → "Blueprint"

3. **Connect Repository**
   - Connect your GitHub account if not already connected
   - Select repository: `Ambreeen17/TO-DO-APP-PHASE1`
   - Branch: `phase-2`
   - Render will detect the `render.yaml` file automatically

4. **Review Configuration**
   - Service name: `todo-backend`
   - Database name: `todo-db`
   - Region: Oregon
   - Plan: Free

5. **Deploy**
   - Click "Apply" to create services
   - Render will:
     - Create PostgreSQL database
     - Build and deploy the backend
     - Auto-generate JWT_SECRET
     - Set up CORS_ORIGINS

6. **Get Backend URL**
   - After deployment completes, you'll get a URL like:
   - `https://todo-backend-xxxx.onrender.com`
   - Copy this URL for frontend configuration

### Option 2: Deploy via Render CLI

1. **Install Render CLI**
   ```bash
   npm install -g render
   ```

2. **Login to Render**
   ```bash
   render login
   ```

3. **Deploy from render.yaml**
   ```bash
   cd backend
   render deploy
   ```

### Environment Variables (Auto-configured)

The `render.yaml` file automatically configures:

| Variable | Value | Source |
|----------|-------|--------|
| `JWT_SECRET` | Auto-generated | Render |
| `CORS_ORIGINS` | `https://frontend-ordvthoae-ambreen-rais-projects.vercel.app` | render.yaml |
| `DATABASE_URL` | Auto-configured | PostgreSQL service |

### Update CORS Origins After Deployment

If you change the frontend URL, update `CORS_ORIGINS`:

1. Go to Render Dashboard → `todo-backend` service
2. Navigate to "Environment" tab
3. Update `CORS_ORIGINS` value
4. Click "Save Changes" (triggers auto-redeploy)

---

## Frontend Deployment (Vercel)

### Current Status
✅ **Already Deployed**: https://frontend-ordvthoae-ambreen-rais-projects.vercel.app

### Update Backend URL

After backend is deployed on Render:

1. **Get Render Backend URL**
   - Example: `https://todo-backend-xxxx.onrender.com`

2. **Update Vercel Environment Variable**
   - Go to: https://vercel.com/ambreen-rais-projects/frontend
   - Navigate to "Settings" → "Environment Variables"
   - Add/Update:
     ```
     NEXT_PUBLIC_API_URL=https://todo-backend-xxxx.onrender.com
     ```
   - Click "Save"

3. **Redeploy Frontend**
   - Go to "Deployments" tab
   - Click "..." on latest deployment → "Redeploy"
   - Or push a new commit to trigger auto-deployment

### Alternative: Update via CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Add environment variable
vercel env add NEXT_PUBLIC_API_URL production

# Redeploy
vercel --prod
```

---

## Testing Deployment

### 1. Test Backend Health
```bash
curl https://todo-backend-xxxx.onrender.com/docs
```
Expected: Swagger UI documentation page

### 2. Test Backend API
```bash
# Register a user
curl -X POST https://todo-backend-xxxx.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Login
curl -X POST https://todo-backend-xxxx.onrender.com/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

### 3. Test Frontend
1. Visit: https://frontend-ordvthoae-ambreen-rais-projects.vercel.app
2. Click "Sign up" → Create account
3. Login with credentials
4. Create a task
5. Verify task appears in list

---

## Troubleshooting

### Backend Issues

**Issue**: Build fails on Render
- **Solution**: Check Python version in `render.yaml` matches `requirements.txt`
- Verify all dependencies are listed in `requirements.txt`

**Issue**: Database connection fails
- **Solution**: Ensure `DATABASE_URL` is correctly linked in `render.yaml`
- Check PostgreSQL service is running

**Issue**: CORS errors in browser console
- **Solution**: Update `CORS_ORIGINS` in Render environment variables
- Add your frontend URL to the comma-separated list

### Frontend Issues

**Issue**: Frontend can't connect to backend
- **Solution**: Verify `NEXT_PUBLIC_API_URL` is set in Vercel
- Check backend URL is accessible (no typos)

**Issue**: Authentication not working
- **Solution**: Clear browser cookies and localStorage
- Re-login with fresh credentials

---

## Monitoring

### Render Dashboard
- View logs: Dashboard → Service → Logs
- Monitor metrics: Dashboard → Service → Metrics
- Check database: Dashboard → Database → Connections

### Vercel Dashboard
- View deployments: https://vercel.com/ambreen-rais-projects/frontend
- Check build logs: Deployments → [deployment] → Build Logs
- Monitor analytics: Analytics tab

---

## Cost Considerations

### Render Free Tier
- ✅ Free PostgreSQL: 1GB storage, 97 connection hours/month
- ✅ Free Web Service: Sleeps after 15 min inactivity
- ⚠️ First request after sleep takes ~30 seconds (cold start)

### Vercel Free Tier
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Automatic SSL certificates

---

## Production Checklist

- [x] Backend deployed on Render
- [x] PostgreSQL database configured
- [x] Environment variables set
- [x] Frontend deployed on Vercel
- [x] Frontend connected to backend
- [ ] Custom domain configured (optional)
- [ ] Monitoring alerts set up (optional)
- [ ] Backup strategy defined (optional)

---

## Next Steps

### Phase 3: AI-Powered Layer
After successful deployment, proceed to Phase 3:
- Natural language task creation
- AI chat interface
- Smart suggestions

### Production Hardening (Optional)
- Set up custom domain
- Configure production database backups
- Add monitoring and alerts
- Implement rate limiting
- Set up error tracking (Sentry)
