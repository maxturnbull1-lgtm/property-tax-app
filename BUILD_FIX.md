# Fixing Koyeb Build Error (Exit Code 51)

If you're getting build error code 51 on Koyeb, try these fixes:

## Solution 1: Remove Custom Build Commands (Recommended)

**The most common cause**: Custom build commands interfere with buildpacks.

1. Go to your Koyeb service settings
2. **Remove any custom build commands** (leave empty)
3. Buildpacks will automatically:
   - Detect Python from `requirements.txt`
   - Install dependencies
   - Use `Procfile` for running

## Solution 2: Verify File Structure

Ensure these files are in the root of your repository:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Startup command
- ✅ `runtime.txt` - Python version (optional)
- ✅ `app.py` - Main application file

## Solution 3: Check Requirements.txt Format

Make sure `requirements.txt`:
- Has no empty lines at the end
- Uses compatible package versions
- All packages are available on PyPI

## Solution 4: Use Buildpack Build Method

In Koyeb:
1. Go to Service → Settings → Build
2. Ensure **"Buildpack"** is selected (not Dockerfile)
3. Buildpack should auto-detect Python

## Solution 5: Check Build Logs

In Koyeb dashboard:
1. Go to your service
2. Click "Logs" tab
3. Look at build logs for specific error messages
4. Common issues:
   - Package installation failures
   - Version conflicts
   - Missing system dependencies

## Solution 6: Pin Python Version

If issues persist, ensure `runtime.txt` specifies a Python version:
```
python-3.9.18
```

## Still Having Issues?

1. Check Koyeb logs for specific error messages
2. Verify all files are committed to GitHub
3. Try a fresh deployment with empty build/run commands
4. Contact Koyeb support with build logs
