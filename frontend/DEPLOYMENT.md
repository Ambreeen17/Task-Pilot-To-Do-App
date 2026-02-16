# Vercel Deployment Instructions

## Frontend Deployment

### Option 1: Update Existing Project
1. Go to your Vercel project dashboard
2. Go to **Settings** → **General**
3. Set **Root Directory** to: `frontend`
4. Save and redeploy

### Option 2: Create New Project
1. Go to: https://vercel.com/new
2. Import repository: `Ambreeen17/TO-DO-APP-PHASE1`
3. Select branch: `phase-2`
4. In **Configure Project**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
5. Click **Deploy**

## Environment Variables

After deployment, add these in Vercel → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=your-backend-api-url-here
```

Example (when backend is deployed):
```
NEXT_PUBLIC_API_URL=https://your-backend-api.vercel.app
```

## Backend Deployment

The backend (FastAPI) needs to be deployed separately:

1. Create a new Vercel project for the backend
2. Set **Root Directory** to: `backend`
3. Add environment variables:
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   JWT_SECRET=your-secure-random-string-here
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ```
4. Deploy

## Testing

After both are deployed:
1. Access frontend URL
2. Try signing up
3. Try creating a task
4. Verify API calls work correctly

## Common Issues

**Module not found error**: Ensure Root Directory is set to `frontend`

**API connection errors**: Check NEXT_PUBLIC_API_URL is set correctly

**CORS errors**: Ensure CORS_ORIGINS in backend matches frontend URL
