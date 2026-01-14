# Web Scraper Troubleshooting Guide

## Common Issues on Live Deployment

### Issue: Scraper Not Working on Koyeb/Cloud

#### Solution 1: Check Fast HTTP Lookup
The app tries HTTP lookup first (fastest, no browser needed). This should work in most cases.

**What to check:**
- Look at the debug output - does it show "HTTP (Fast)" method?
- Check if the address format is correct
- Verify the site is accessible from the cloud server

#### Solution 2: Browser Automation Issues

If HTTP lookup fails, the app tries:
1. Selenium with Chrome
2. Playwright with Chromium (fallback)

**Common problems:**
- Chrome not installed properly
- Missing system libraries
- Sandbox issues in containers

**Fixes applied:**
- ✅ All required libraries in Dockerfile
- ✅ Playwright as automatic fallback
- ✅ Better error handling and retry logic

#### Solution 3: Check Logs

In Koyeb dashboard:
1. Go to Service → Logs
2. Look for error messages
3. Check if Chrome/Playwright is starting
4. Look for "Fast lookup error" messages

### Debugging Steps

1. **Check which method is being used:**
   - Look for "_method" in debug output
   - HTTP (Fast) = Best, no browser needed
   - Selenium/Playwright = Browser automation

2. **Verify address format:**
   - Should include: Street, City, State, ZIP
   - Example: "4524 Glory Way SW, Wyoming, MI 49418"

3. **Check network connectivity:**
   - The cloud server needs internet access
   - HometownLocator.com must be reachable

4. **Review error messages:**
   - Expand "Debug Information" in the app
   - Check technical details
   - Look for specific error patterns

### Quick Fixes

1. **Redeploy with latest code:**
   ```bash
   git pull
   # Koyeb will auto-redeploy
   ```

2. **Check environment:**
   - Verify PORT is set correctly
   - Check if IS_CLOUD is detected properly

3. **Test locally first:**
   - Run `streamlit run app.py` locally
   - See if scraper works on your machine
   - Compare with cloud behavior

### If Nothing Works

1. Check Koyeb logs for detailed errors
2. Verify all dependencies are installed
3. Try a different address format
4. Contact support with error logs
