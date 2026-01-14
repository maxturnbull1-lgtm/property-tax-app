# Fixing Chrome Binary Not Found Error on Koyeb

## Problem
Error: `cannot find Chrome binary`

This happens when Selenium can't locate Chrome/Chromium on the Koyeb server.

## Solution 1: Ensure Aptfile is Configured

Make sure `Aptfile` exists in the root of your repository with:
```
chromium-browser
chromium-chromedriver
```

Koyeb will automatically install these packages during build if you're using the Apt buildpack.

## Solution 2: Enable Apt Buildpack on Koyeb

In Koyeb dashboard:
1. Go to your Service → Settings → Build
2. Make sure buildpacks are in this order:
   - `heroku/buildpacks:apt` (or similar Apt buildpack)
   - `heroku/buildpack-python` (Python buildpack)
3. The Apt buildpack reads `Aptfile` and installs system packages

## Solution 3: Use Dockerfile Instead (Alternative)

If buildpacks continue to fail, create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Install Chrome and dependencies
RUN apt-get update && \
    apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Solution 4: Verify Chrome Installation

The updated `cloud_scraper.py` now:
- Searches multiple Chrome binary locations
- Uses `which` command as fallback
- Provides better error messages

## Quick Fix Checklist

- [ ] `Aptfile` exists with `chromium-browser` and `chromium-chromedriver`
- [ ] Apt buildpack is enabled in Koyeb
- [ ] Service is redeployed after adding Aptfile
- [ ] Check build logs to verify Chrome is installed

## Still Having Issues?

1. Check Koyeb build logs to see if Chrome packages installed
2. Try using Dockerfile deployment instead of buildpacks
3. Consider using Playwright instead of Selenium (handles browser installation better)
