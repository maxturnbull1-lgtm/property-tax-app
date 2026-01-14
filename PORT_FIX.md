# Fixing Port 8000 Health Check Issue

## Problem
Koyeb health check fails on port 8000 - app not responding.

## Solution Applied

### 1. Updated Dockerfile
- Now uses `${PORT:-8000}` to use PORT environment variable
- Defaults to port 8000 if PORT is not set
- Exposes port 8000

### 2. Updated Procfile
- Uses `${PORT:-8000}` with default to 8000
- Compatible with buildpack deployments

### 3. Updated koyeb.json
- Specifies `http_port: 8000` in deploy section
- Routes configured for port 8000

## In Koyeb Dashboard

If health checks still fail:

1. **Go to Service → Settings → Health Checks**
2. **Configure Health Check**:
   - **Path**: `/` or `/_stcore/health`
   - **Port**: `8000`
   - **Interval**: `30s` (or default)
   - **Timeout**: `10s`
   - **Grace Period**: `60s`

3. **Verify Environment Variables**:
   - Go to Service → Settings → Environment
   - Make sure `PORT=8000` is set (Koyeb usually sets this automatically)

## Alternative: Manual Port Configuration

If automatic port detection doesn't work:

1. Go to Service → Settings → Environment
2. Add environment variable: `PORT=8000`
3. Redeploy

## Verify App is Running

After redeployment, check logs:
```bash
# In Koyeb dashboard → Logs
# Should see: "You can now view your Streamlit app in your browser"
# Should see: "Network URL: http://0.0.0.0:8000"
```

## Still Having Issues?

1. Check build logs - ensure Dockerfile built successfully
2. Check runtime logs - verify Streamlit started on port 8000
3. Try accessing the app directly to see if it's running
4. Verify koyeb.json configuration is being read
